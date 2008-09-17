#!/usr/local/bin/python

'''
#
# Report:
#
#	NCBI Gene Models with no Marker Association
#
#       Produce a tab-delimited report with the following output fields:
#
#       NCBI Gene Model ID
#
# Usage:
#       MRK_NoNCBI.py
#
# lec	05/08/2008
#	- TR 8966; Build 37
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
fp.write('# NCBI Gene Models with no Marker Association\n')
fp.write('#\n')

# get the full set of NCBI gene model ids
# we exclude the obsolete vega ids (only include status = active)
# we exclude all but type protein_coding and pseudogene
db.sql('select accID ' + \
    'into #ncbiGeneModel ' + \
    'from ACC_Accession  a, SEQ_Sequence s ' + \
    'where a._lOGicalDB_key = 59 ' + \
    'and a._MGIType_key = 19 ' + \
    'and a._Object_key = s._Sequence_key ' + \
    'and s._SequenceStatus_key = 316342 ' + \
    'and (s.description like "%protein_coding%" or s.description like "%pseudogene%")', None)
db.sql('create index idxAccid on #ncbiGeneModel(accID)', None)

# get the set of NCBI ids with marker associations
db.sql('select distinct accID ' + \
    'into #ncbiGeneAssoc ' + \
    'from ACC_Accession  ' + \
    'where _LogicalDB_key = 59 ' + \
    'and _MGIType_key = 2 ' + \
    'and preferred = 1', None)
db.sql('create index idxAccid on #ncbiGeneAssoc(accID)', None)

results = db.sql('select gm.accid as ncbiGeneModelNoAssoc ' + \
    'from #ncbiGeneModel gm ' + \
    'where not exists (select 1 ' + \
    'from #ncbiGeneAssoc ga ' + \
    'where ga.accid = gm.accid) ' + \
    'order by gm.accID', 'auto')

for r in results:
    fp.write(r['ncbiGeneModelNoAssoc'] + CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.finish_nonps(fp)