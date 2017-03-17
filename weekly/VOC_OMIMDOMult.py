#!/usr/local/bin/python

'''
#
# VOC_OMIMDOMult.py
#
# Report:
#
#       DO terms that have multiple OMIM xrefs
#
# Usage:
# 	VOC_OMIMDOMult.py
#
# Notes:
#
# History:
#
# 11/17/2016	lec
#       - TR12427/Disease Ontology (DO)
#
'''

import sys
import os
import string
import reportlib
import db

db.setTrace()

TAB = reportlib.TAB
CRT = reportlib.CRT

fp = reportlib.init(sys.argv[0], 'DO terms that have multiple OMIM xrefs', outputdir = os.environ['QCOUTPUTDIR'])

db.sql('''
	select a1.accID
	INTO TEMP TABLE doid
	from ACC_Accession a1, ACC_Accession a2
	where a1._MGIType_key = 13
	and a1._LogicalDB_key = 191 
	and a1.preferred = 1 
	and a1._Object_key = a2._Object_key
	and a2._LogicalDB_key = 15
	group by a1.accID having count(*) > 1 
	''', None)
db.sql('create index doid_idx on doid(accID)', None)

results = db.sql('''
	select a1.accID as doid, a2.accID as omimid, a3.accID as genotypeid
	from ACC_Accession a1, ACC_Accession a2, VOC_Annot va, ACC_Accession a3
	where a1._MGIType_key = 13
	and a1._LogicalDB_key = 191 
	and a1.preferred = 1 
	and a1._Object_key = a2._Object_key
	and a2._LogicalDB_key = 15
	and a1._Object_key = va._Term_key
	and va._AnnotType_key = 1020
	and va._Object_key = a3._Object_key
	and a3._MGIType_key = 12
	and a3.prefixPart = 'MGI:'
	and exists (select 1 from doid where a1.accID = doid.accID)
	order by a1.accID, a2.accID
	''', 'auto')

for r in results:
	fp.write(r['doid'] + TAB)
	fp.write(r['omimid'] + TAB)
	fp.write(r['genotypeid'] + CRT)

fp.write('\n(%d rows affected)\n\n' % (len(results)))

reportlib.finish_nonps(fp)

