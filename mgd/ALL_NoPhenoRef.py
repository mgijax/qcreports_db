#!/usr/local/bin/python

'''
#
# TR 10126
#
# Report:
#
#	Alleles that are involved in a genotype
#       that has an annotation containing 
#           "no phenotypic analysis" MP:0003012 
#           "no abnormal phenotype detected" MP:0002169 
#       contains references where reference type in 
#           indexed
#           priority indexed
#
# Usage:
#       ALL_NoPhenoRef.py
#
# Notes:
#
# History:
#
# 03/16/2010	lec
#	- TR10126/modify this report to include two additional columns.  
#         Please include a column for "allele type" and a column for the total number of 
#         additional references ("indexed" plus "priority indexed", same as column A in 
#         report 18 above).
#
# 02/04/2010	lec
#	- original TR10024; sql report
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

fp = reportlib.init(sys.argv[0], 'Alleles that are involved in genotypes where:', os.environ['QCOUTPUTDIR'])

fp.write(2*TAB + '  annotations contain' + CRT)
fp.write(2*TAB + '       no phenotypic analysis, MP:0003012' + CRT)
fp.write(2*TAB + '       no abnormal phenotype detected, MP:0002169' + 2*CRT)
fp.write(2*TAB + '  references contain' + CRT)
fp.write(2*TAB + '       indexed' + CRT)
fp.write(2*TAB + '       priority indexed' + 2*CRT)

fp.write(string.ljust('symbol', 50))
fp.write(string.ljust('term', 40))
fp.write(string.ljust('allele type', 40))
fp.write(string.ljust('additional references', 40))
fp.write(CRT)

fp.write(string.ljust('----------------------------------------', 50))
fp.write(string.ljust('-----------------------------------', 40))
fp.write(string.ljust('-----------------------------------', 40))
fp.write(string.ljust('---------------------', 40))
fp.write(CRT)

db.sql('''select distinct m._Object_key, count(m._Refs_key) as counter
          into temporary table refA
          from MGI_Reference_Assoc m, MGI_RefAssocType t
          where m._MGIType_key = 11
          and m._RefAssocType_key = t._RefAssocType_key
          and t.assocType in ('Priority Index', 'Indexed')
	  group by m._Object_key
	  ''', None)
db.sql('create index refA_idx on refA(_Object_key)', None)
results = db.sql('select * from refA', 'auto')
refA = {}
for r in results:
    refA[r['_Object_key']] = r['counter']

# only interested in the A group
results = db.sql('''select distinct aa._Allele_key, aa.symbol, 
		    substring(t.term, 1, 35) as term,
                    substring(tt.term, 1, 35) as alleleType
             from ALL_Allele aa, GXD_AlleleGenotype g, VOC_Annot a, VOC_Term t, VOC_Term tt
             where aa._Allele_key = g._Allele_key
             and g._Genotype_key = a._Object_key
             and a._AnnotType_key = 1002
             and a._Term_key in (83412,293594)
             and a._Term_key = t._Term_key
             and aa._Allele_Type_key = tt._Term_key
             and exists (select 1 from refA r where aa._Allele_key = r._Object_key)
             order by aa.symbol
	     ''', 'auto')

for r in results:

    alleleKey = r['_Allele_key']
    fp.write(string.ljust(r['symbol'], 50))
    fp.write(string.ljust(r['term'], 40))
    fp.write(string.ljust(r['alleleType'], 40))
    a = int(refA[alleleKey])
    fp.write(str(a) + CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.finish_nonps(fp)

