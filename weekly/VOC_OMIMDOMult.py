#!/usr/local/bin/python

'''
#
# VOC_OMIMDOMult.py
#
# Report:
#
#       OMIM-to-Genotype Annotations that do not map to DO
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
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

TAB = reportlib.TAB
CRT = reportlib.CRT

fp = reportlib.init(sys.argv[0], 'DO terms that have mulitple OMIM xrefs', outputdir = os.environ['QCOUTPUTDIR'])

results = db.sql('''
	select a1.accID
	from ACC_Accession a1, ACC_Accession a2
	where a1._MGIType_key = 13
	and a1._LogicalDB_key = 191 
	and a1._Object_key = a2._Object_key
	and a1.preferred = 1 
	and a2._LogicalDB_key = 15
	group by a1.accID having count(*) > 1 
	order by a1.accID
	''', 'auto')

for r in results:
	fp.write(r['accID'] + CRT)

fp.write('\n(%d rows affected)\n\n' % (len(results)))

reportlib.finish_nonps(fp)

