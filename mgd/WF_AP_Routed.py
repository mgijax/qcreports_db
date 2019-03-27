#!/usr/local/bin/python

'''
#
# TR12250/Lit Triage
#
# Report:
#
#	The reference must be:
#	group = AP, status = 'Not Routed'
#	for other groups, there must be at least one status in:
#		'Routed', 'Chosen', 'Indexed', 'Full-coded'
#	not discarded
#
#	output:
#	1. J#
#	2. Creation Date
#	3. status/group : 1 row per group
#	4. extracted text (80 characters/around text)
#
# Usage:
#       WF_AP_Routed.py
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

fp = reportlib.init(sys.argv[0], 'Review for AP routed workflow status', os.environ['QCOUTPUTDIR'])

searchTerms = [
'targeted mutation',
'knockout mouse',
'knockout mice',
'knock-out mouse',
'knock-out mice',
'knockin mouse',
'knockin mice',
'knock-in mouse',
'knock-in mice',
'transgene',
'transgenic mouse',
'transgenic mice',
'induced mutation',
'spontaneous mutant',
'mutant mouse',
'mutant mice',
'heterozygote',
'homozygote',
'crispr',
'-/-'
]

fp.write('''
 	The reference must be:
 	     group = AP, status = 'Not Routed'
 	     for other groups, there must be at least one status in:
 		     'Routed', 'Chosen', 'Indexed', 'Full-coded'
 	     not discarded
''')
fp.write('\n\tterm search:\n' + str(searchTerms) + '\n\n')

byDate = {}
byStatus = {}
byText = {}

searchSQL = ''
for s in searchTerms:
	searchSQL += ' lower(d.extractedText) like lower(\'%' + s + '%\') or'
searchSQL = searchSQL[:-2]

# read in all extracted text that matches
# exclude extractedText not in 'reference' section
sql = '''
select r._Refs_key, c.jnumID, lower(d.extractedText) as extractedText,
	to_char(r.creation_date, 'MM/dd/yyyy') as cdate
into temp table extractedText
from BIB_Refs r, BIB_Citation_Cache c, BIB_Workflow_Data d
where r.isDiscard = 0
and r._Refs_key = c._Refs_key
and r._Refs_key = d._Refs_key
and d._ExtractedText_key not in (48804491)
and d.extractedText is not null

and exists (select wfso._Refs_key from BIB_Workflow_Status wfso
        where r._Refs_key = wfso._Refs_key
        and wfso._Group_key in (31576664)
        and wfso._Status_key in (31576669)
        and wfso.isCurrent = 1
        )

and exists (select wfso._Refs_key from BIB_Workflow_Status wfso
        where r._Refs_key = wfso._Refs_key
        and wfso._Group_key not in (31576664)
        and wfso._Status_key not in (31576669, 31576672)
        and wfso.isCurrent = 1
        )

'''

db.sql(sql, None)
db.sql('create index ref_idx on extractedText(_Refs_key)', None)

#
# process extracted text
#
results = db.sql('select * from extractedText', 'auto')
for r in results:

	jnumID = r['jnumID']

	if jnumID not in byDate:
	    byDate[jnumID] = []
            byDate[jnumID].append(r['cdate'])

	if jnumID not in byText:
	    byText[jnumID] = []

	extractedText = r['extractedText']
	extractedText = extractedText.replace('\n', ' ')
	extractedText = extractedText.replace('\r', ' ')
	for s in searchTerms:
	    for match in re.finditer(s, extractedText):
		subText = extractedText[match.start()-40:match.end()+40]
                if len(subText) == 0:
		    subText = extractedText[match.start()-10:match.end()+40]
                byText[jnumID].append(subText)

#
# process group/status
#
sql = '''
select r._Refs_key, r.jnumID, concat(g.abbreviation||'|'||s.term) as groupstatus
from extractedText r, BIB_Workflow_Status wfs, VOC_Term g, VOC_Term s
where r._Refs_key = wfs._Refs_key
and wfs._Group_key = g._Term_key
and wfs._Status_key = s._Term_key
and wfs.isCurrent = 1
order by groupstatus
'''
results = db.sql(sql, 'auto')

for r in results:

	jnumID = r['jnumID']
	groupstatus = r['groupstatus']

	if jnumID not in byStatus:
	    byStatus[jnumID] = []
	if groupstatus not in byStatus[jnumID]:
            byStatus[jnumID].append(groupstatus)

#
# print report
#
counter = 0
keys = byStatus.keys()
keys.sort()
for r in keys:
	if len(byText[r]) > 0:
	    fp.write(r + TAB)
	    fp.write(byDate[r][0] + TAB)
	    fp.write('\t'.join(byStatus[r]) + TAB)
	    fp.write('|'.join(byText[r]) + CRT)
	    counter += 1

fp.write('\n(%d rows affected)\n' % counter)
reportlib.finish_nonps(fp)

