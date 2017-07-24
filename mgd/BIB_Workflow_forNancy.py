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

curatorExclude = 'MGI:curator_%'
discardExclude = 'MGI:Discard'
notSelectedExclude = 'Tumor:NotSelected'

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
	and not exists (select 1 from BIB_Workflow_Tag wt, VOC_Term wtt
		where r._Refs_key = wt._Refs_key
		and wt._Tag_key = wtt._Term_key
		and wtt.term like '%s'
		)
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
sys.exit(0)

login = 'jfinger'
#login = 'csmith'
#login = 'dph'
#login = 'dmk'
results = db.sql('''
	select t._Term_key, t.abbreviation 
	from MGI_User u, VOC_Term t
	where u.login = '%s'
	and u._Group_key = t._Term_key
	''' % (login), 'auto')
for r in results:
    groupKey = r['_Term_key']
    group = r['abbreviation']

if group == 'AP':
    masterjournals = ajournals
elif group == 'GXD':
    masterjournals = gjournals
elif group == 'GO':
    masterjournals = ojournals
elif group == 'Tumor':
    masterjournals = tjournals
elif group == 'QTL':
    masterjournals = 'None'

results = db.sql('''
	(
	select r.mgiID
	from BIB_Citation_Cache r
	where r.journal in (%s)
	and exists (select 1 from BIB_Workflow_Status ws, VOC_Term wst
		where r._Refs_key = ws._Refs_Key
		and ws._Status_key = wst._Term_key
		and wst.term in ('Not Routed')
		and ws._Group_key = %s
		)
	and not exists (select 1 from BIB_Workflow_Tag wt, VOC_Term wtt
		where r._Refs_key = wt._Refs_key
		and wt._Tag_key = wtt._Term_key
		and wtt.term like '%s'
		)
	union
	select r.mgiID
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
	and not exists (select 1 from BIB_Workflow_Tag wt, VOC_Term wtt
		where r._Refs_key = wt._Refs_key
		and wt._Tag_key = wtt._Term_key
		and wtt.term like '%s'
		)
	)
	order by mgiID
	limit 200
	'''  % (masterjournals, groupKey, curatorExclude, ajournals, ojournals, gjournals, tjournals, curatorExclude), 'auto')

for r in results:
	fp.write(str(r) + '\n')

fp.write('\n%s rows()' % (len(results)))

reportlib.finish_nonps(fp)

