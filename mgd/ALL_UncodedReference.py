#!/usr/local/bin/python

'''
#
# TR 10023
#
# Report:
#
#	Alleles with most uncoded references
#
#	A = # of priority indexed + indexed
#	B = # of used-fc + not used + expression only + reviewed
#	ration of A/B
#
# Usage:
#       ALL_UncodedReference.py
#
# Notes:
#
# History:
#
# 03/16/2010	lec
#	- TR10126/modify this report such that column "B" is only counting "Used-FC" references 
#         and exclude ""not used" + "expression only" + "reviewed" from the count.
#
# 02/04/2010	lec
#       - created
#
'''
 
import sys 
import os 
import string
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Alleles with most uncoded references', os.environ['QCOUTPUTDIR'])

fp.write('     A = # of "priority indexed" + "indexed"' + CRT)
fp.write('     B = # of "used-fc"' + CRT)
fp.write('     ration of A/B' + 2*CRT)

db.sql('''select distinct m._Object_key, counter = count(m._Refs_key)
          into #refA
          from MGI_Reference_Assoc m, MGI_RefAssocType t
          where m._MGIType_key = 11
          and m._RefAssocType_key = t._RefAssocType_key
          and t.assocType in ('Priority Index', 'Indexed')
	  group by m._Object_key
	  ''', None)
db.sql('create index idx1 on #refA(_Object_key)', None)
results = db.sql('select * from #refA', 'auto')
refA = {}
for r in results:
    refA[r['_Object_key']] = r['counter']

db.sql('''select distinct m._Object_key, counter = count(m._Refs_key)
          into #refB
          from MGI_Reference_Assoc m, MGI_RefAssocType t
          where m._MGIType_key = 11
          and m._RefAssocType_key = t._RefAssocType_key
          and t.assocType in ('Used-FC')
	  group by m._Object_key
	  ''', None)
db.sql('create index idx1 on #refB(_Object_key)', None)
results = db.sql('select * from #refB', 'auto')
refB = {}
for r in results:
    refB[r['_Object_key']] = r['counter']

# only interested in the A group
results = db.sql('''select distinct a._Allele_key, a.symbol 
		    from ALL_Allele a
		    where exists (select 1 from #refA r where a._Allele_key = r._Object_key)
		    order by a.symbol
                 ''', 'auto')

for r in results:

     alleleKey = r['_Allele_key']
     fp.write(string.ljust(r['symbol'], 50))

     a = 0
     b = 0

     if refA.has_key(alleleKey):
	 a = int(refA[alleleKey])
         fp.write(str(a) + TAB)
     else:
         fp.write('0' + TAB)

     if refB.has_key(alleleKey):
	 b = int(refB[alleleKey])
         fp.write(str(b) + TAB)
     else:
         fp.write('0' + TAB)

     if b > 0:
         fp.write(str(a/b) + CRT)
     else:
         fp.write(CRT)

reportlib.finish_nonps(fp)

