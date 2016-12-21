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
# History
#
# 12/21/2011	lec
#	- convert to outer join
#
# 09/26/2011	sc
#	TR10866/ include GM if no raw biotype; needed outer join
#
# 03/07/2011	lec
#	TR626/add rawbiotype from SEQ_GeneModel
#
'''
 
import sys 
import os
import reportlib
import db

db.setTrace()

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
fp.write('# field 1: ensembl gene model accession id\n')
fp.write('# field 2: raw biotype\n')
fp.write('#\n')

# get the full set of VEGA gene model ids
# we exclude the obsolete vega ids (only include status = active)
db.sql('''select accID, s._Sequence_key
    into temporary table vegaGeneModel
    from ACC_Accession  a, SEQ_Sequence s
    where a._lOGicalDB_key = 85
    and a._MGIType_key = 19
    and a._Object_key = s._Sequence_key
    and s._SequenceStatus_key = 316342
    ''', None)
db.sql('create index idxAccid1 on vegaGeneModel(accID)', None)
db.sql('create index idxSeqKey1 on vegaGeneModel(_Sequence_key)', None)

# get the set of VEGA ids with marker associations
db.sql('''select distinct accID 
    into temporary table vegaGeneAssoc 
    from ACC_Accession  
    where _LogicalDB_key = 85 
    and _MGIType_key = 2
    and preferred = 1
    ''', None)
db.sql('create index idxAccid2 on vegaGeneAssoc(accID)', None)
results = db.sql('''select gm.accid as vegaGeneModelNoAssoc, s.rawbiotype 
    from vegaGeneModel gm
	 LEFT OUTER JOIN SEQ_GeneModel s on (gm._Sequence_key = s._Sequence_key)
    where not exists (select 1 
    from vegaGeneAssoc ga 
    where ga.accid = gm.accid) 
    order by gm.accID
    ''', 'auto')

for r in results:
    fp.write(r['vegaGeneModelNoAssoc'] + TAB)
    raw = r['rawbiotype']
    if raw == None:
	raw = ''
    fp.write(raw + CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.finish_nonps(fp)
