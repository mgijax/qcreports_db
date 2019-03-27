#!/usr/local/bin/python

'''
#
# TR13031/Lit Triage/AP/isDiscard = yes
#
# Report:
#
#	The reference must be:
#	group = AP, isDiscard = 1
#
#	output:
#	1. MGI ID
#	2. 'mice' count
#	3. count of matching terms
#	4. last user to modify reference
#	5. creation date of reference
#	6. extracted text (80 characters/around text)
#
# Usage:
#       WF_AP_Disarc.py
#
# Notes:
#
# History:
#
# 01/31/2019
#	- TR13031/Lit Triage/AP/isDiscard = yes
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

fp = reportlib.init(sys.argv[0], 'Review for AP discard = yes', os.environ['QCOUTPUTDIR'])

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
 	     group = AP, isDiscard = yes
	     exclude : AP:DiscardReviewed

	1. MGI ID
	2. 'mice' count
	3. count of matching terms
	4. last user to modify reference
	5. creation date of reference
	6. extracted text (80 characters/around text)
''')
fp.write('\n\tterm search:\n' + str(searchTerms) + '\n\n')

byUser = {}
byMGI = {}
byText = {}
byMiceCount = {}

# iterate thru each searchTerm
# this other option is to do a set of "or" for each searchTerm
# but this was taking forever, so switched to this method

searchSQL = ''

results = db.sql('''
	select r._Refs_key, c.mgiID, 
		to_char(r.creation_date, 'MM/dd/yyyy') as cdate,
		u.login,
		lower(d.extractedText) as extractedText
	from BIB_Refs r, BIB_Citation_Cache c, BIB_Workflow_Status wfs, MGI_User u, BIB_Workflow_Data d
	where r.isDiscard = 1
	and r._Refs_key = c._Refs_key
	and r._ModifiedBy_key = u._User_key
	and r._Refs_key = wfs._Refs_key 
	and wfs._Group_key = 31576664
	and wfs.isCurrent = 1
	and not exists (select 1 from BIB_Workflow_Tag wft 
		where r._Refs_key = wft._Refs_key 
		and wft._Tag_key = 48188429
		)

	and r._Refs_key = d._Refs_key
	and d._ExtractedText_key not in (48804491)
	and d.extractedText is not null
	''', 'auto')

for r in results:

	mgiID = r['mgiID']

	if mgiID not in byUser:
	    byUser[mgiID] = []
        byUser[mgiID].append((r['login'], r['cdate']))

	if mgiID not in byMGI:
	    byMGI[mgiID] = []
        byMGI[mgiID].append(mgiID)

	if mgiID not in byText:
	    byText[mgiID] = []

        # find the place in the extractText where the searchTerm exists
	# take a slice around the begin/end part of the extractedText
	extractedText = r['extractedText']
	extractedText = extractedText.replace('\n', ' ')
	extractedText = extractedText.replace('\r', ' ')

        for s in searchTerms:
	    for match in re.finditer(s, extractedText):
	        subText = extractedText[match.start()-40:match.end()+40]
		if len(subText) == 0:
	            subText = extractedText[match.start()-10:match.end()+40]
                byText[mgiID].append(subText)

	# count number of times the term 'mice" appears in the extractedText
	# only have to do this once per mgiID/reference
	# even if mgiID/reference appears > 1 in results
	if mgiID not in byMiceCount:
	    mcount = 0
            byMiceCount[mgiID] = []
	    for match in re.finditer('mice', extractedText):
                mcount += 1
	    byMiceCount[mgiID].append(mcount)

keys = byMGI.keys()
keys.sort()
for r in keys:

    if len(byText[r]) > 0:
        fp.write(r + TAB)
        fp.write(str(byMiceCount[r][0]) + TAB)
        fp.write(str(len(byText[r])) + TAB)
        fp.write(byUser[r][0][0] + TAB)
        fp.write(byUser[r][0][1] + TAB)
        fp.write('|'.join(byText[r]) + CRT)

fp.write('\n(%d rows affected)\n' % (len(byMGI)))
reportlib.finish_nonps(fp)

