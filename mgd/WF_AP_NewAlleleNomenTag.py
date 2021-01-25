
'''
#
# TR12250/Lit Triage
#
# Report:
#
#	Review for AP:NewAlleleNomenclature tag
#
#       The reference must be:
#            group = AP, status = 'Routed' or 'Chosen'
#            group = AP, tag != 'AP:NewAlleleNomenclature'
#                    and tag != 'AP:NewTransgene'
#                    and tag != ‘AP:New_allele_New_gene’
#	not discarded
#
#	output:
#	1. J#
#	2. Creation Date
#	3. status/group : 1 row per group
#	4. extracted text (80 characters/around text)
#
# Usage:
#       WF_AP_NewAlleleNomenTag.py
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

fp = reportlib.init(sys.argv[0], 'Review for AP:NewAlleleNomenclature tag', os.environ['QCOUTPUTDIR'])

searchTerms = [
'we generated', 
'we have generated', 
'we created', 
'we have created', 
'mice were generated', 
'mice were created', 
'targeting vector', 
' es cell', 
'targeting construct', 
'generation of mice', 
'generation of mutant mice', 
'generation of transgenic mice'
]

searchTerms = [x.lower() for x in searchTerms]

fp.write('''
        The reference must be:
             group = AP, status = 'Routed' or 'Chosen'
             group = AP, tag != 'AP:NewAlleleNomenclature'
                     and tag != 'AP:NewTransgene'
                     and tag != 'AP:New_allele_New_gene'
             not discarded
''')
fp.write('\n\tterm search:\n' + str(searchTerms) + '\n\n')

byDate = {}
byStatus = {}
byText = {}

# read non-null extracted text
# exclude extractedText not in 'reference' section
sql = '''
select r._Refs_key, c.mgiid, c.jnumid, lower(d.extractedText) as extractedText,
        to_char(r.creation_date, 'MM/dd/yyyy') as cdate
into temp table extractedText
from BIB_Refs r, BIB_Citation_Cache c, BIB_Workflow_Data d, BIB_Workflow_Relevance v
where r._Refs_key = v._Refs_key
and v._Relevance_key != 70594666
and v.isCurrent = 1
and r._Refs_key = c._Refs_key
and r._Refs_key = d._Refs_key
and d._ExtractedText_key not in (48804491)
and d.extractedText is not null

and exists (select wfso._Refs_key from BIB_Workflow_Status wfso
        where r._Refs_key = wfso._Refs_key
        and wfso._Group_key in (31576664)
        and wfso._Status_key in (31576670, 31576671)
        and wfso.isCurrent = 1
        )

and not exists (select wftag._Refs_key from BIB_Workflow_Tag wftag
        where r._Refs_key = wftag._Refs_key
        and wftag._Tag_key in (31576700, 31576702, 35710200)
        )
'''

db.sql(sql, None)
db.sql('create index ref_idx on extractedText(_Refs_key)', None)

#
# process extracted text
#
results = db.sql('select * from extractedText', 'auto')
for r in results:

        mgiid = r['mgiid']

        if mgiid not in byDate:
            byDate[mgiid] = []
            byDate[mgiid].append(r['cdate'])

        if mgiid not in byText:
            byText[mgiid] = []

        extractedText = r['extractedText']
        extractedText = extractedText.replace('\n', ' ')
        extractedText = extractedText.replace('\r', ' ')
        for s in searchTerms:
            for match in re.finditer(s, extractedText):
                subText = extractedText[match.start()-40:match.end()+40]
                if len(subText) == 0:
                    subText = extractedText[match.start()-10:match.end()+40]
                byText[mgiid].append(subText)

#
# process group/status
#
sql = '''
select r._Refs_key, r.mgiid, r.jnumid, concat(g.abbreviation||'|'||s.term) as groupstatus
from extractedText r, BIB_Workflow_Status wfs, VOC_Term g, VOC_Term s
where r._Refs_key = wfs._Refs_key
and wfs._Group_key = g._Term_key
and wfs._Status_key = s._Term_key
and wfs.isCurrent = 1
order by groupstatus
'''
results = db.sql(sql, 'auto')

for r in results:

        mgiid = r['mgiid']
        groupstatus = r['groupstatus']

        if mgiid not in byStatus:
            byStatus[mgiid] = []
        if groupstatus not in byStatus[mgiid]:
            byStatus[mgiid].append(groupstatus)

#
# print report
#
counter = 0
keys = list(byStatus.keys())
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
