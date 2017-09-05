#!/usr/local/bin/python

'''
#
# TR12250/Lit Triage
#
# Report:
#
#	Review for AP:NewDiseaseModel tag
#
#	The reference must be:
#	group = AP, status = 'Routed', 'Chosen'
#	group = AP, tag != 'AP:NewDiseaseModel'
#	not discarded
#
#	output:
#	1. J#
#	2. Creation Date
#	3. status/group : 1 row per group
#	4. extracted text (80 characters/around text)
#
# Usage:
#       WF_AP_NewDiseaseModelTag.py
#
# Notes:
#
# History:
#
# 09/29/2017
#	- TR12250/Lit Triage
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

fp = reportlib.init(sys.argv[0], 'Review for AP:NewDiseaseModel tag', os.environ['QCOUTPUTDIR'])

searchTerms = [
'model for',
'model of',
'disease model',
'syndrome',
'candidate gene',
'susceptibility gene',
'disease condition'
]

fp.write('''
 	The reference must be:
 	     group = AP, status = 'Routed' or 'Chosen'
 	     group = AP, tag != 'AP:NewDiseaseModel'
 	     not discarded
''')
fp.write('\n\tterm search:\n' + str(searchTerms) + '\n\n')

byJData = {}
byJStatus = {}
byJText = {}

searchSQL = ''
for s in searchTerms:
	searchSQL += ' lower(d.extractedText) like lower(\'%' + s + '%\') or'
searchSQL = searchSQL[:-2]

results = db.sql('''
select r._Refs_key, c.jnumID, g.abbreviation as groupTerm, s.term as statusTerm, d.extractedText,
	to_char(r.creation_date, 'MM/dd/yyyy') as cdate
from BIB_Refs r, BIB_Citation_Cache c, BIB_Workflow_Status wfs, BIB_Workflow_Data d, 
	VOC_Term g, VOC_Term s
where r.isDiscard = 0
and r._Refs_key = c._Refs_key
and r._Refs_key = d._Refs_key
and r._Refs_key = wfs._Refs_key
and wfs._Group_key = g._Term_key
and wfs._Status_key = s._Term_key
and wfs.isCurrent = 1

and exists (select wfso._Refs_key from BIB_Workflow_Status wfso
	where r._Refs_key = wfso._Refs_key
	and wfso._Group_key in (31576664)
	and wfso._Status_key in (31576670, 31576671)
	and wfso.isCurrent = 1
	)

and not exists (select wftag._Refs_key from BIB_Workflow_Tag wftag
	where r._Refs_key = wftag._Refs_key
	and wftag._Tag_key in (31576701)
	)

and (%s)
order by jnumID, groupTerm
''' % (searchSQL), 'auto')

for r in results:
	jnumID = r['jnumID']
	groupstatus = r['groupTerm'] + '|' + r['statusTerm'] + TAB

	if jnumID not in byJData:
	    byJData[jnumID] = []
        byJData[jnumID].append(r['cdate'])

	if jnumID not in byJStatus:
	    byJStatus[jnumID] = []
        byJStatus[jnumID].append(groupstatus)

	if jnumID not in byJText:
	    byJText[jnumID] = []
	    addExtractedText = 1
	else:
	    addExtractedText = 0

	if addExtractedText == 0:
	    continue

	extractedText = r['extractedText']
	extractedText = extractedText.replace('\n', ' ')
	extractedText = extractedText.replace('\r', ' ')
	for s in searchTerms:
	    for match in re.finditer(s, extractedText):
		subText = extractedText[match.start()-40:match.end()+40]
                byJText[jnumID].append(subText)

keys = byJStatus.keys()
keys.sort()
for r in keys:
	fp.write(r + TAB)
	fp.write(byJData[r][0] + TAB)
	fp.write('\t'.join(byJStatus[r]) + TAB)
	fp.write('|'.join(byJText[r]) + CRT)

fp.write('\n(%d rows affected)\n' % (len(byJStatus)))
reportlib.finish_nonps(fp)

