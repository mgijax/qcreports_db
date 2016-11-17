#!/usr/local/bin/python

'''
#
# VOC_OMIMDOObsolete.py
#
# Report:
#
#       Obsolete OMIM terms in DO as xrefs
#
# Usage:
# 	VOC_OMIMDOObsolete.py
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
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

TAB = reportlib.TAB
CRT = reportlib.CRT

fp = reportlib.init(sys.argv[0], 'Obsolete OMIM terms in DO as xrefs', outputdir = os.environ['QCOUTPUTDIR'])

results = db.sql('''
	(
	select a1.accID as doid, a2.accID as omimid
	from ACC_Accession a1, ACC_Accession a2
	where a1._MGIType_key = 13
	and a1._LogicalDB_key = 191 
	and a1._Object_key = a2._Object_key
	and a1.preferred = 1 
	and a2._LogicalDB_key = 15
	and not exists (select 1 from ACC_Accession a3, VOC_Term t
		where a2.accID = a3.accID
		and a3._MGIType_key = 13
		and a3._LogicalDB_key = 15
		and a3._Object_key = t._Term_key
		and t._Vocab_key = 44
		)
	union
	select a1.accID as doid, a2.accID as omimid
	from ACC_Accession a1, ACC_Accession a2
	where a1._MGIType_key = 13
	and a1._LogicalDB_key = 191 
	and a1._Object_key = a2._Object_key
	and a1.preferred = 1 
	and a2._LogicalDB_key = 15
	and exists (select 1 from ACC_Accession a3, VOC_Term t
		where a2.accID = a3.accID
		and a3._MGIType_key = 13
		and a3._LogicalDB_key = 15
		and a3._Object_key = t._Term_key
		and t._Vocab_key = 44
		and t.isObsolete = 1
		)
	)
	order by doid
	''', 'auto')

for r in results:
	fp.write(r['doID'] + TAB)
	fp.write(r['omimID'] + CRT)

fp.write('\n(%d rows affected)\n\n' % (len(results)))

reportlib.finish_nonps(fp)

