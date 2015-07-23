#!/usr/local/bin/python

'''
#
# TR 10523
#
# Report:
#
#	A list of Markers of Type "gene"
#	where the Marker's Allele of status "approved"
#	contain Genotypes that contain MP Annotations
#
#	output:
#	1. MGI ID of the marker (type = gene)
#	2. marker symbol
#	3. # of alleles
#	4. # of MP annotations
#	5. list of MP J#'s from column 4
#
# Usage:
#       ALL_MPAnnot.py
#
# Notes:
#
# History:
#
# 02/13/2011
#	- TR10589/add feature type
#
# 01/20/2011	lec
#       - created
#
'''
 
import sys 
import os 
import string
import reportlib
import db

db.setTrace()
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Total MP Annotations per Gene', os.environ['QCOUTPUTDIR'])

fp.write('includes:\n')
fp.write('    markers of type "gene"\n')
fp.write('    alleles of status "approved"\n')
fp.write('    alleles that are annotated to the MP\n\n')
fp.write('field 1: MGI id\n')
fp.write('field 2: marker symbol\n')
fp.write('field 3: marker feature type\n')
fp.write('field 4: # of alleles\n')
fp.write('field 5: # of MP annotations\n')
fp.write('field 6: list of MP J# from column 4\n\n')

#
# markers with 
#   marker type 'gene'
#   alleles of status = 'approved'
#   contain MP annotations
#
db.sql('''
	select distinct m._Marker_key, m.symbol
	into temporary table markers
        from MRK_Marker m
        where m._Marker_Type_key = 1
	and exists (select 1 from ALL_Allele aa, GXD_AlleleGenotype p, VOC_Annot v
            where m._Marker_key =  p._Marker_key
	    and p._Allele_key = aa._Allele_key
	    and aa._Allele_Status_key = 847114
            and p._Genotype_key = v._Object_key
            and v._AnnotType_key = 1002)
       ''', None)
db.sql('create index markers_idx on markers(_Marker_key)', None)

# marker ids

mgiIDs = {}
results = db.sql('''select m._Marker_key, a.accID
	    from markers m, ACC_Accession a 
	    where m._Marker_key = a._Object_key 
	    and a._LogicalDB_key = 1 
	    and a._MGIType_key = 2
	    and a.prefixPart = 'MGI:'
	    and a.preferred = 1
	    ''', 'auto')
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    mgiIDs[key] = value

#
# marker feature type
#
mgiFeature = {}
results = db.sql('''
           select m._Marker_key, t.term
           from markers m, VOC_Annot a, VOC_Term t
           where m._Marker_key = a._Object_key
           and a._AnnotType_key = 1011
           and a._Term_key = t._Term_key
        ''', 'auto')
for r in results:
    key = r['_Marker_key']
    value = r['term']
    mgiFeature[key] = value

#
# alleles by gene
# count of alleles
# count of annotations
# grouped by marker
#
totalAllele = {}
totalAnnot = {}
results = db.sql('''
	select m._Marker_key, 
	       count(distinct aa._Allele_key) as totalAllele,
	       count(distinct v._Annot_key) as totalAnnot
        from markers m, ALL_Allele aa, GXD_AlleleGenotype p, VOC_Annot v
            where m._Marker_key =  p._Marker_key
	    and p._Allele_key = aa._Allele_key
	    and aa._Allele_Status_key = 847114
            and p._Genotype_key = v._Object_key
            and v._AnnotType_key = 1002
	    group by m._Marker_key
       ''', 'auto')
for r in results:
    key = r['_Marker_key']
    totalAllele[key] = r['totalAllele']
    totalAnnot[key] = r['totalAnnot']

# annotation references by gene
refsID = {}
results = db.sql('''
        select distinct m._Marker_key, c.accID 
        from markers m, ALL_Allele aa, GXD_AlleleGenotype p, 
	     VOC_Annot v, VOC_Evidence e, ACC_Accession c
	where m._Marker_key =  p._Marker_key
	and p._Allele_key = aa._Allele_key
	and aa._Allele_Status_key = 847114
        and p._Genotype_key = v._Object_key
        and v._AnnotType_key = 1002
        and v._Annot_key = e._Annot_key
        and e._Refs_key = c._Object_key 
        and c._LogicalDB_key = 1 
        and c._MGIType_key = 1
        and c.prefixPart = 'J:'
        and c.preferred = 1
     ''', 'auto')
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not refsID.has_key(key):
	refsID[key] = []
    refsID[key].append(value)

# final output to print
results = db.sql('''
	select distinct m._Marker_key, m.symbol from markers m order by symbol
	''', 'auto')

fp.write('total # of genes:  ' + str(len(results)) + 2*CRT)

for r in results:

    key = r['_Marker_key']

    fp.write(mgiIDs[key] + TAB)
    fp.write(r['symbol'] + TAB)

    if mgiFeature.has_key(key):
      fp.write(mgiFeature[key])
    fp.write(TAB)

    fp.write(str(totalAllele[key]) + TAB)
    fp.write(str(totalAnnot[key]) + TAB)
    fp.write(string.join(refsID[key],  ',') + CRT)

reportlib.finish_nonps(fp)

