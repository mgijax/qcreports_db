
'''
#
# TR12777/Lit Triage Supplemental Data Needed
#
# Report:
#
# 	References where:
#	- has J#
#	- is not Discard
#	- is-reviewe-article = No
#	- supplemental in:
#		'Db found supplement'
#		'Curator found supplement'
#	- Status in ('Chosen', 'Indexed')
#	- Journal not in 'Elife'
#
#	because the J: assignment triggered a search for:
#	- supplemental
#	- supplementary
#	- additional file
#	- Supplement_
#	- Appendix
#	- supporting information
#
#	output:
#	1. J#
#
#
# order by MGI_User._UserType_key; Curator or DBO, Data Load
# then Status ('Chosen', 'Indexed')
# then JnumID
#
# Usage:
#       WF_SupplementalData
#
# Notes:
#
# History:
#
# 02/14/2018
#	- TR12777/Lit Triage Supplemental Data Needed
#
'''
 
import sys 
import os 
import re
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

fp = reportlib.init(sys.argv[0], 'Supplemental Data Needed', os.environ['QCOUTPUTDIR'])

fp.write('\tReferences where:\n')
fp.write('\t- has J#\n')
fp.write('\t- is not Discard\n')
fp.write('\t- is-reviewe-article = No\n')
fp.write('\t- supplemental in:\n')
fp.write('\t\tDb found supplement\n')
fp.write('\t\tCurator found supplement\n')
fp.write('\t- Status in (Chosen, Indexed)\n')
fp.write('\t- Journal not in "Elife"\n')
fp.write('\t- Sorted by Curator/pm2geneload, Status, J#\n\n')
fp.write('\tbecause the J: assignment triggered a search for:\n')
fp.write('\t- supplemental\n')
fp.write('\t- supplementary\n')
fp.write('\t- additional file\n')
fp.write('\t- Supplement_\n')
fp.write('\t- Appendix\n')
fp.write('\t- supporting information\n\n')

curatorList = []
results = db.sql('''
select distinct r.jnumID, t.term
from BIB_Citation_Cache r, BIB_Workflow_Data d, BIB_Workflow_Status s, BIB_Workflow_Relevance v, VOC_Term t, MGI_User u
where r._Refs_key = v._Refs_key
and v._Relevance_key != 70594666
and v.isCurrent = 1
and r.isReviewArticle = 0
and r.jnumID is not null
and r.journal not in ('Elife')
and r._Refs_key = d._Refs_key
and d._Supplemental_key in (31576675, 34027000)
and d._ExtractedText_key = 48804490
and r._Refs_key = s._Refs_key
and s.isCurrent = 1
and s._Status_key in (31576671, 31576673)
and s._Status_key = t._Term_key
and s._createdby_key = u._User_key
and u._UserType_key in (316352, 316354)
order by t.term, r.jnumID
''', 'auto')
for r in results:
    jnumID = r['jnumID']
    if jnumID not in curatorList:
        curatorList.append(jnumID)

dataloadList = []
results = db.sql('''
select distinct r.jnumID, t.term
from BIB_Citation_Cache r, BIB_Workflow_Data d, BIB_Workflow_Status s, BIB_Workflow_Relevance v, VOC_Term t, MGI_User u
where r._Refs_key = v._Refs_key
and v._Relevance_key != 70594666
and v.isCurrent = 1
and r.isReviewArticle = 0
and r.jnumID is not null
and r.journal not in ('Elife')
and r._Refs_key = d._Refs_key
and d._Supplemental_key in (31576675, 34027000)
and d._ExtractedText_key = 48804490
and r._Refs_key = s._Refs_key
and s.isCurrent = 1
and s._Status_key in (31576671, 31576673)
and s._Status_key = t._Term_key
and s._createdby_key = u._User_key
and u._UserType_key = 316353
order by t.term, r.jnumID
''', 'auto')
for r in results:
    jnumID = r['jnumID']
    if jnumID not in curatorList and jnumID not in dataloadList:
        dataloadList.append(jnumID)

for r in curatorList:
    fp.write(r + CRT)
for r in dataloadList:
    fp.write(r + CRT)

totalCount = len(curatorList) + len(dataloadList)
fp.write('\n(%d rows affected)\n' % (totalCount))
reportlib.finish_nonps(fp)
