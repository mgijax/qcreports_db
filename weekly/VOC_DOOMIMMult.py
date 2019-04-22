#!/usr/local/bin/python

'''
#
# VOC_OMIMDOMult.py
#
# Report:
#
#       OMIM terms that have multiple DO xrefs
#
# Usage:
# 	VOC_DOOMIMMult.py
#
# Notes:
#
# History:
#
# 04/09/2019	sc
#       - TR13075 OMIM terms xref'ed to multiple DO terms
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
PIPE = '|'

fp = reportlib.init(sys.argv[0], 'OMIM terms that have multiple DO xrefs', outputdir = os.environ['QCOUTPUTDIR'])

results = db.sql('''
	WITH includeOMIM AS (
	select a2.accID
        from ACC_Accession a1, ACC_Accession a2
        where a1._MGIType_key = 13
        and a1._LogicalDB_key = 191
        and a1._Object_key = a2._Object_key
        and a1.preferred = 1
        and a2._LogicalDB_key = 15
        group by a2.accID having count(*) > 1
        )
        select distinct a1.accID as doid, a2.accID as omimid, a2.numericPart, t.term as doterm
        from includeOMIM d, ACC_Accession a1, VOC_Term t, ACC_Accession a2
        where d.accID = a2.accID
        and t._Vocab_key = 125
        and t._Term_key = a1._Object_key
        and a1._LogicalDB_key = 191
	and a1.preferred = 1
        and a1._Object_key = a2._Object_key
        and a2._LogicalDB_key = 15''', 'auto')

omimDict = {}

for r in results:
    omimid = r['omimid']
    doid =  r['doid']
    doterm = r['doterm']
    if omimid not in omimDict:
	omimDict[omimid] = []
    omimDict[omimid].append('%s%s%s' % (doid, PIPE, doterm))

for omimid in sorted(omimDict.keys()):
    doList = omimDict[omimid]
    for d in doList:
	doid, doterm = string.split(d, '|')
	fp.write(omimid + TAB)
	fp.write(doid + TAB)
	fp.write(doterm + CRT)

fp.write('\n(%d rows affected)\n\n' % (len(results)))

reportlib.finish_nonps(fp)

