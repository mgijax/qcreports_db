
'''
#
# TR12779
#
# Report:
# List specimens in recombinase reporter assays (assay type = 10) 
# whose genotypes have only a single allele pair.
#
# Fields:
# J# (of assay)
# Assay id
# Specimen label
# Genotype id
# Allele1
# Allele2
#
# The primary sort should be Assay id in reverse chronological order.
# The secondary sort should be Specimen label in alphabetical order.
#
# Title for the new report:
# "Recombinase reporter specimen genotype check."
#
# Usage:
#       RECOMB_ReporterCheck.py
#
# Notes:
#
# History:
#
# lec	05/01/2008
#	- new; TR 8775; copy from GXD
#
'''

import sys
import os
import re
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#

fp = reportlib.init(sys.argv[0], '\nRecombinase reporter specimen genotype check', \
        os.environ['QCOUTPUTDIR'])

# get all recombinase reporter speciments
db.sql('''
    select distinct a._Assay_key, a1.accid as jNum, substring(specimenLabel, 
        1, 50) as specimenLabel, e._Genotype_key
    INTO TEMPORARY TABLE reporter
    from GXD_Assay a, GXD_Specimen s, GXD_Expression e, ACC_Accession a1
    where a._AssayType_key  = 11
    and a._Assay_key = s._Assay_key
    and a._Assay_key = e._Assay_key
    and a._Refs_key = a1._Object_key
    and a1._MGIType_key = 1
    and a1._LogicalDB_key = 1
    and a1.preferred = 1
    and a1.prefixPart = 'J:' ''', None)

db.sql('''
    create index idx1 on reporter(_Genotype_key)''', None)

# Get all genotypes with single allele pairs
db.sql('''
    select distinct _Genotype_key
    into temporary table sglAllelePair
    from GXD_AllelePair ap
    group by _Genotype_key
    having count(*) = 1''', None)

db.sql('''
    create index idx2 on sglAllelePair(_Genotype_key)
  ''', None)

# get specimens with single allele pairs, get allele1, genotype and assay IDs
db.sql('''
    select r.*, al1.symbol as allele1, ap._Allele_key_2, a1.accid as genotypeID, a2.accid as assayID
    into temporary table specSglAllelePair
    from reporter r, sglAllelePair sap, GXD_AllelePair ap, ACC_Accession a1, ACC_Accession a2, ALL_Allele al1
    where r._Genotype_key = sap._Genotype_key
    and sap._Genotype_key = ap._Genotype_key
    and ap._Genotype_key = a1._Object_key
    and a1._MGIType_key = 12
    and a1._LogicalDB_key = 1
    and a1.preferred = 1
    and a1.prefixPart = 'MGI:'
    and r._Assay_key = a2._Object_key
    and a2._MGIType_key = 8
    and a2._LogicalDB_key = 1
    and a2.preferred = 1
    and a2.prefixPart = 'MGI:'
    and ap._Allele_key_1 = al1._Allele_key''', None)

db.sql('''
    create index idx3 on specSglAllelePair(_Genotype_key) ''', None)

# get allele2
results = db.sql('''
    select s.jNum, s.assayID, s.specimenLabel, s.genotypeID, 
        s._Genotype_key, s.allele1, al2.symbol as allele2
    from specSglAllelePair s
    left outer join ALL_Allele al2 on (s._Allele_key_2 = al2._Allele_key)
    order by s._Assay_key DESC, s.specimenLabel''', 'auto')

fp.write('jNum%sassayID%sspecimenLabel%sgenotypeID%sallele1%sallele2%s' % (TAB, TAB, TAB, TAB, TAB, CRT))
count = 0
for r in results:
    count = count + 1
    jNum = r['jNum']
    assayID = r['assayID']
    specLabel = r['specimenLabel']
    genoID = r['genotypeID']
    allele1 = r['allele1']
    allele2 = r['allele2']
    if allele2 == None:
        allele2 = ''
    fp.write('%s%s%s%s%s%s%s%s%s%s%s%s' % (jNum, TAB, assayID, TAB, specLabel, TAB, genoID, TAB, allele1, TAB, allele2, CRT))

fp.write('Number of specimens: ' + str(count) + 2*CRT)

reportlib.finish_nonps(fp)
