#!/usr/local/bin/python

'''
#
# Report:
#
#	VEGA Gene Models with no Marker Association
#
#       Produce a tab-delimited report with the following output fields:
#
#       VEGA Gene Model ID
#
# Usage:
#       MRK_NoVEGA.py
#
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

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

fp.write('#\n')
fp.write('# VEGA Gene Models with no Marker Association\n')
fp.write('#\n')

# get the full set of VEGA gene model ids
# we exclude the obsolete vega ids (only include status = active)
db.sql('select accID ' + \
    'into #vegaGeneModel ' + \
    'from ACC_Accession  a, SEQ_Sequence s ' + \
    'where a._lOGicalDB_key = 85 ' + \
    'and a._MGIType_key = 19 ' + \
    'and a._Object_key = s._Sequence_key ' + \
    'and s._SequenceStatus_key = 316342', None)
db.sql('create index idxAccid on #vegaGeneModel(accID)', None)

# get the set of VEGA ids with marker associations
db.sql('select distinct accID ' + \
    'into #vegaGeneAssoc ' + \
    'from ACC_Accession  ' + \
    'where _LogicalDB_key = 85 ' + \
    'and _MGIType_key = 2 ' + \
    'and preferred = 1', None)
db.sql('create index idxAccid on #vegaGeneAssoc(accID)', None)
results = db.sql('select gm.accid as vegaGeneModelNoAssoc ' + \
    'from #vegaGeneModel gm ' + \
    'where not exists (select 1 ' + \
    'from #vegaGeneAssoc ga ' + \
    'where ga.accid = gm.accid) ' + \
    'order by gm.accID', 'auto')

for r in results:
    fp.write(r['vegaGeneModelNoAssoc'] + CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.finish_nonps(fp)
