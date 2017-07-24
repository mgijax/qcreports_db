#!/usr/local/bin/python

'''
#
# BIB_Workflow_forNancy.py
#
# Report:
#
# History:
#
# 07/21/2017	lec
#       - TR12250/Lit Triage
#
#
'''
 
import sys 
import os
import string
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

apJournals = [
'Nat Neurosci',
'Neurobiol Aging',
'Neuroscience'
]

goJournals = [
'J Biol Chem',
'Biochem J'
]

gxdJournals = [
'Development',
'Dev Biol',
'Dev Dyn',
'Mech Dev',
'Genes Dev',
'Gene Expr Patterns',
'Dev Cell',
'BMC Dev Biol'
]

tumorJournals= [
'Cancer Cell',
'Cancer Discov',
'Cancer Lett',
'Cancer Res',
'Carcinogenesis',
'Int J Cancer',
'J Natl Cancer Inst',
'Leukemia',
'Mol Cancer Res',
'Nat Rev Cancer',
'Oncogene',
'Semi Cancer Biol'
]

#
# Main
#

fp = reportlib.init(sys.argv[0], printHeading = None, outputdir = os.environ['QCOUTPUTDIR'])

ajournals = '\'' + '\',\''.join(apJournals) + '\''
ojournals = '\'' + '\',\''.join(goJournals) + '\''
gjournals = '\'' + '\',\''.join(gxdJournals) + '\''
tjournals = '\'' + '\',\''.join(tumorJournals) + '\''

countQuery = '''
	select count(r.*) as rCount
	from BIB_Citation_Cache r, BIB_Workflow_Status ws, MGI_User u, VOC_Term wst, VOC_Term gt
	where u._Group_key = ws._Group_key
	and ws._Refs_key = r._Refs_Key
	and r.journal in (%s)
	and ws._Status_key = wst._Term_key
	and wst.term in ('Not Routed')
	and u._Group_key = gt._Term_key
	and gt.abbreviation = '%s'
	'''

results = db.sql(countQuery % (ajournals, 'AP'), 'auto')
for r in results:
	fp.write('A&P journals  :  ' + str(r['rCount']) + '\n')
results = db.sql(countQuery % (gjournals, 'GXD'), 'auto')
for r in results:
	fp.write('GXD journals  :  ' + str(r['rCount']) + '\n')
results = db.sql(countQuery % (ojournals, 'GO'), 'auto')
for r in results:
	fp.write('GO journals   :  ' + str(r['rCount']) + '\n')
results = db.sql(countQuery % (tjournals, 'Tumor'), 'auto')
for r in results:
	fp.write('Tumor journals:  ' + str(r['rCount']) + '\n')
fp.write('\n\n')

results = db.sql('''
	(
	select r.mgiID, r.journal, r._Refs_key, 1 as orderby
	from BIB_Citation_Cache r
	where r.journal in (%s)
	and exists (select 1 from BIB_Workflow_Status ws, VOC_Term wst, MGI_User u
		where r._Refs_key = ws._Refs_Key
		and ws._Status_key = wst._Term_key
		and wst.term in ('Not Routed')
		and u.login = 'jfinger'
		and u._Group_key = ws._Group_key
		)
	union
	select r.mgiID, r.journal, r._Refs_key, 2
	from BIB_Citation_Cache r
	where r.journal not in (%s)
	and r.journal not in (%s)
	and r.journal not in (%s)
	and r.journal not in (%s)
	and exists (select 1 from BIB_Workflow_Status ws, VOC_Term wst
		where r._Refs_key = ws._Refs_Key
		and ws._Status_key = wst._Term_key
		and wst.term in ('Not Routed')
		and ws._Group_key = 31576664
		)
	and exists (select 1 from BIB_Workflow_Status ws, VOC_Term wst
		where r._Refs_key = ws._Refs_Key
		and ws._Status_key = wst._Term_key
		and wst.term in ('Not Routed')
		and ws._Group_key = 31576665
		)
	and exists (select 1 from BIB_Workflow_Status ws, VOC_Term wst
		where r._Refs_key = ws._Refs_Key
		and ws._Status_key = wst._Term_key
		and wst.term in ('Not Routed')
		and ws._Group_key = 31576666
		)
	and exists (select 1 from BIB_Workflow_Status ws, VOC_Term wst
		where r._Refs_key = ws._Refs_Key
		and ws._Status_key = wst._Term_key
		and wst.term in ('Not Routed')
		and ws._Group_key = 31576667
		)
	and exists (select 1 from BIB_Workflow_Status ws, VOC_Term wst
		where r._Refs_key = ws._Refs_Key
		and ws._Status_key = wst._Term_key
		and wst.term in ('Not Routed')
		and ws._Group_key = 31576668
		)
	)
	order by orderby, mgiID
	limit 200
	'''  % (gjournals, ajournals, ojournals, gjournals, tjournals), 'auto')

for r in results:
	fp.write(str(r) + '\n')

print fp.write('\n%s rows()' % (len(results)))

reportlib.finish_nonps(fp)

