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
# dbm   12/6/2002
#       - created
#
'''
 
import sys 
import os 
import db
import reportlib

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
            'exists (select * ' + \
                    'from ALL_Allele a ' + \
                    'where m._Marker_key = a._Marker_key and ' + \
                          'a.symbol not like "%<+>") and ' + \
            'not exists (select * ' + \
                        'from MRK_Notes n ' + \
                        'where m._Marker_key = n._Marker_key) ' + \
      'order by ac.accID, m.symbol'

results = db.sql(cmd, 'auto')

for r in results:
        fp.write(r['accID'] + TAB + r['symbol'] + CRT)

fp.write(CRT + 'Number of Genes: ' + str(len(results)) + CRT)

reportlib.finish_nonps(fp)
