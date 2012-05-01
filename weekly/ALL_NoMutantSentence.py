#!/usr/local/bin/python

'''
#
# TR 4297
#
# Report:
#       Produce a report of genes with phenotypic alleles and no
#       mutant sentence.  Display the following tab-demilited fields:
#
#       MGI_ID    Gene_Symbol
#
# Usage:
#       tr4297.py
#
# Notes:
#
# History:
#
# lec	01/26/2010
#	- TR 10019
#
#       The revised report should include those markers where
#       marker type = gene
#       and where the gene has one or more phenotypic allele(s)
#       and where at least one of the phenotypic allele(s) has MP terms
#       and where a "marker clip" does not exist for the gene
#
# 05/14/2009
#	- TR9405/gene trap less filling
#	- only include genes that have at least one genotype
#	- only include genes that have at least on MP annotation
#
# dbm   12/6/2002
#       - created
#
'''
 
import sys 
import os 
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

fp = reportlib.init(sys.argv[0], 'Genes w/Phenotypic Alleles and No Mutant Sentence', os.environ['QCOUTPUTDIR'])

cmd = 'select ac.accID, m.symbol ' + \
      'from ACC_Accession ac, MRK_Marker m ' + \
      'where ac._Object_key = m._Marker_key and ' + \
            'ac.prefixPart = "MGI:" and ' + \
            'ac.preferred = 1 and ' + \
            'ac._MGIType_key = 2 and ' + \
            'ac._LogicalDB_key = 1 and ' + \
            'm._Marker_Type_key = 1 and ' + \
            'exists (select 1 ' + \
                    'from ALL_Allele a ' + \
                    'where m._Marker_key = a._Marker_key and ' + \
                          'a.isWildType = 0) and ' + \
            'exists (select 1 ' + \
                    'from GXD_AlleleGenotype a, VOC_Annot va ' + \
                    'where m._Marker_key = a._Marker_key ' + \
		    'and a._Genotype_key = va._Object_key ' + \
		    'and va._AnnotType_key = 1002) and ' + \
            'not exists (select 1 ' + \
                        'from MRK_Notes n ' + \
                        'where m._Marker_key = n._Marker_key) ' + \
      'order by ac.accID, m.symbol'

results = db.sql(cmd, 'auto')

for r in results:
        fp.write(r['accID'] + TAB + r['symbol'] + CRT)

fp.write(CRT + 'Number of Genes: ' + str(len(results)) + CRT)

reportlib.finish_nonps(fp)
