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
# History
#
# 12/21/2011	lec
#	- convert to outer join
#
# 09/26/2011    sc
#       TR10866/ include GM if no raw biotype; needed outer join
#
# 03/07/2011	lec
#	TR626/add rawbiotype from SEQ_GeneModel
#
# 02/10/2011	lec
#	TR10541/remove "protein_coding" and "pseudogene" exclusions
#
# 01/19/2011	lec
#	TR10541/added history/fix 'lOG'/added exclude/include into to header
#
# 05/17/2007	sc
# 	TR8304 ensembl release 44 
#	update to exclude obsoletes and include only protein_coding and pseudogene
#
'''
 
import sys 
import os
import reportlib
import db

db.setTrace()
db.setAutoTranslateBE()

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
fp.write('# excludes obsoletes\n')
fp.write('# field 1: ensembl gene model accession id\n')
fp.write('# field 2: raw biotype\n')
fp.write('#\n')

#
# get the full set of Ensembl gene model ids
# we exclude the obsolete vega ids (only include status = active)
# TR10541: remove
# 'and (s.description like "%protein_coding%" or s.description like "%pseudogene%")', None)
#

db.sql('''select a.accID, s._Sequence_key
    into temporary table ensemblGeneModel 
    from ACC_Accession  a, SEQ_Sequence s 
    where a._LogicalDB_key = 60 
    and a._MGIType_key = 19 
    and a._Object_key = s._Sequence_key 
    and s._SequenceStatus_key = 316342
    ''', None)
db.sql('create index ensembl_idxAccid on ensemblGeneModel(accID)', None)
db.sql('create index ensembl_idxSeqkey on ensemblGeneModel(_Sequence_key)', None)
print "done first query and index"

# get the set of Ensembl ids with marker associations
db.sql('''select distinct accID 
    into temporary table ensemblGeneAssoc 
    from ACC_Accession  
    where _LogicalDB_key = 60 
    and _MGIType_key = 2 
    and preferred = 1
    ''', None)
db.sql('create index idxAccid on ensemblGeneAssoc(accID)', None)
print "done second query and index"

results = db.sql('''select gm.accid as ensemblGeneModelNoAssoc, s.rawbiotype
    from ensemblGeneModel gm 
	 LEFT OUTER JOIN SEQ_GeneModel s on (gm._Sequence_key = s._Sequence_key)
    where not exists (select 1 
    from ensemblGeneAssoc ga 
    where ga.accid = gm.accid) 
    order by gm.accID
    ''', 'auto')
print "done third query and writing out results"

for r in results:
    fp.write(r['ensemblGeneModelNoAssoc'] + TAB)
    raw = r['rawbiotype']
    if raw == None:
	raw = ''
    fp.write(raw + CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.finish_nonps(fp)
