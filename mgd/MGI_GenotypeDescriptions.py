#!/usr/local/bin/python

'''
#
# MGI_GenotypeDescriptions.py
#
# Report:
#
#	Tab-delimited report where a row in the report
#	represents:
#
#	field 1: Gene ID
#	field 2: Gene Symbol
#	field 3: Allele ID
#	field 4: Allele Symbol
#	field 5: Genotype ID
#	field 6: Alleles
#	field 7: Genetic Background
#
# Usage:
#       MGI_GenotypeDescriptions.py
#
# History:
#
# sc	02/16/2012
#	-TR9766 - turned this customSQL into a report
#
'''
 
import sys 
import os
import string
import re
import reportlib

try:
    if os.environ['DB_TYPE'] == 'postgres':
        import pg_db
        db = pg_db
        db.setTrace()
        db.setAutoTranslateBE()
    else:
        import db
except:
    import db


CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

db.useOneConnection(1)
fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

#
# retrieve all genotypes
#

db.sql('''
	select distinct a._Genotype_key, a._Marker_key, a.symbol, 
        a._Allele_key_1, a.allele1, g._Strain_key 
        into #genotypes 
        from GXD_AllelePair_View a, GXD_Genotype g 
        where a._Genotype_key = g._Genotype_key
	''', None)

db.sql('create index genotypes_idx1 on #genotypes(_Genotype_key)', None)
db.sql('create index genotypes_idx2 on #genotypes(_Marker_key)', None)
db.sql('create index genotypes_idx3 on #genotypes(_Allele_key_1)', None)

#
# retrieve MGI IDs for genes
#

results = db.sql('''
	select distinct g._Marker_key, m.mgiID 
        from #genotypes g, MRK_Mouse_View m 
        where g._Marker_key = m._Marker_key
	''', 'auto')
geneID = {}

for r in results:
        key = r['_Marker_key']
        value = r['mgiID']
        geneID[key] = value

#
# retrieve MGI IDs for alleles
#

results = db.sql('''
	select distinct g._Allele_key_1, a.mgiID 
        from #genotypes g, ALL_Summary_View a 
        where g._Allele_key_1 = a._Object_key
	''', 'auto')
alleleID = {}

for r in results:
        key = r['_Allele_key_1']
        value = r['mgiID']
        alleleID[key] = value

#
# retrieve MGI IDs for genotypes
#

results = db.sql('''
	select distinct g._Genotype_key, v.mgiID 
        from #genotypes g, GXD_Genotype_View v 
        where g._Genotype_key = v._Genotype_key
	''', 'auto')
genotypeID = {}

for r in results:
        key = r['_Genotype_key']
        value = r['mgiID']
        genotypeID[key] = value

#
# retrieve strain backgrounds for genotypes
#

results = db.sql('''
	select distinct g._Genotype_key, s.strain 
        from #genotypes g, PRB_Strain s 
        where g._Genotype_key = g._Genotype_key 
        and g._Strain_key = s._Strain_key
	''', 'auto')
strain = {}

for r in results:
        key = r['_Genotype_key']
        value = r['strain']
        strain[key] = value

#
# retrieve allele combination display
#

results = db.sql('''
	select distinct a._Genotype_key, nc.note 
        from #genotypes a, MGI_Note n, MGI_NoteChunk nc 
        where a._Genotype_key = n._Object_key 
        and n._NoteType_key = 1016 
        and n._Note_key = nc._Note_key
	''', 'auto')

alleles = {}
for r in results:
        key = r['_Genotype_key']
        value = re.sub('\n', ',', string.strip(r['note']))
        if not alleles.has_key(key):
                alleles[key] = []
        alleles[key].append(value)

results = db.sql('select * from #genotypes order by _Marker_key, _Allele_key_1', 'auto')

fp.write(TAB.join(['Gene ID', 'Gene Symbol', 'Allele ID', 'Allele Symbol', 'Genotype ID', 'Alleles', 'Genetic Background']) + CRT)

for r in results:
        if geneID.has_key(r['_Marker_key']):
                fp.write(geneID[r['_Marker_key']])
	fp.write(TAB)
        if r['symbol'] != None:
	    fp.write(r['symbol'])
	fp.write(TAB)

        if alleleID.has_key(r['_Allele_key_1']):
                fp.write(alleleID[r['_Allele_key_1']] + TAB)

        fp.write(r['allele1'] + TAB)

        if genotypeID.has_key(r['_Genotype_key']):
                fp.write(genotypeID[r['_Genotype_key']] + TAB)

        if alleles.has_key(r['_Genotype_key']):
                fp.write(string.join(alleles[r['_Genotype_key']], ',') + TAB)

        if strain.has_key(r['_Genotype_key']):
                fp.write(strain[r['_Genotype_key']] + CRT)


reportlib.finish_nonps(fp)	# non-postscript file
db.useOneConnection (0)
