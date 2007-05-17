#!/usr/local/bin/python

'''
#
# Report:
#
#	Ensembl Gene Models with no Marker Association
#
#       Produce a tab-delimited report with the following output fields:
#
#       Ensembl Gene Model ID
#
# Usage:
#       MRK_NoENSEMBL.py
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
print "initializing"
fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

fp.write('#\n')
fp.write('# Ensembl Gene Models with no Marker Association\n')
fp.write('#\n')

# get the full set of Ensembl gene model ids
# we exclude the obsolete vega ids (only include status = active)
# we exclude all but type protein_coding and pseudogene
db.sql('select accID ' + \
    'into #ensemblGeneModel ' + \
    'from ACC_Accession  a, SEQ_Sequence s ' + \
    'where a._lOGicalDB_key = 60 ' + \
    'and a._MGIType_key = 19 ' + \
    'and a._Object_key = s._Sequence_key ' + \
    'and s._SequenceStatus_key = 316342 ' + \
    'and (s.description like "%protein_coding%" or s.description like "%pseudogene%")', None)
db.sql('create index idxAccid on #ensemblGeneModel(accID)', None)
print "done first query and index"
# get the set of Ensembl ids with marker associations
db.sql('select distinct accID ' + \
    'into #ensemblGeneAssoc ' + \
    'from ACC_Accession  ' + \
    'where _LogicalDB_key = 60 ' + \
    'and _MGIType_key = 2 ' + \
    'and preferred = 1', None)
db.sql('create index idxAccid on #ensemblGeneAssoc(accID)', None)
print "done second query and index"

results = db.sql('select gm.accid as ensemblGeneModelNoAssoc ' + \
    'from #ensemblGeneModel gm ' + \
    'where not exists (select 1 ' + \
    'from #ensemblGeneAssoc ga ' + \
    'where ga.accid = gm.accid) ' + \
    'order by gm.accID', 'auto')
print "done third query and writing out results"

for r in results:
    fp.write(r['ensemblGeneModelNoAssoc'] + CRT)
    print r['ensemblGeneModelNoAssoc']

fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.finish_nonps(fp)
