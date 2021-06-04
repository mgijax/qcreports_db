
'''
#
# TR12250/Lit Triage
#
# Report:
#
#	Review for AP:NewAlleleNomenclature tag
#
#       The reference must be:
#            group = AP
#            status = 'Routed' or 'Chosen'
#            and tag not like 'AP:%'
#            and tag not like 'COV:%'
#            and reference added after 2018-01-01
#
#	     and not discarded
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
# 05/06/2021
#       WTS2-614/WTS2-615 - add exclusion of 'AP:new_allele_docking_site'
#      'AP:transgene_new_line', 'AP:Indexing_needed', 'AP:NewDiseaseModel'
#       Add indexed genes column
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
             group = AP
             status = 'Routed' or 'Chosen'
             and tag not like 'AP:%'
             and tag not like 'COV:%'
             not discarded
             and reference added after 2018-01-01
''')
fp.write('\n\tterm search:\n' + str(searchTerms) + '\n\n')

byDate = {}
byStatus = {}
byText = {}

# read non-null extracted text
# exclude extractedText not in 'reference' section
sql = '''
select r._Refs_key, c.jnumid, lower(d.extractedText) as extractedText,
      to_char(r.creation_date, 'MM/dd/yyyy') as cdate
into temp table extractedText
from BIB_Refs r, BIB_Citation_Cache c, BIB_Workflow_Data d, BIB_Workflow_Relevance v, BIB_Workflow_Status wfso, BIB_Workflow_Tag wftag, VOC_Term t
where r._Refs_key = v._Refs_key
and v._Relevance_key != 70594666
and v.isCurrent = 1
and r._Refs_key = c._Refs_key
and r._Refs_key = d._Refs_key
and d._ExtractedText_key not in (48804491)
and d.extractedText is not null
and r.creation_date >= '2018-01-01'::date
and r._Refs_key = wfso._Refs_key
        and wfso._Group_key in (31576664)
        and wfso._Status_key in (31576670, 31576671)
        and wfso.isCurrent = 1
        and r._Refs_key = wftag._Refs_key
        and wftag._Tag_key = t._Term_key
        and t.term not like 'COV:%'
        and t.term not like 'AP:%'
'''

db.sql(sql, None)
db.sql('create index ref_idx on extractedText(_Refs_key)', None)

#
# process extracted text
#
results = db.sql('select * from extractedText', 'auto')
for r in results:

        jnumid = r['jnumid']

        if jnumid not in byDate:
            byDate[jnumid] = []
            byDate[jnumid].append(r['cdate'])

        if jnumid not in byText:
            byText[jnumid] = []

        extractedText = r['extractedText']
        extractedText = extractedText.replace('\n', ' ')
        extractedText = extractedText.replace('\r', ' ')
        for s in searchTerms:
            for match in re.finditer(s, extractedText):
                subText = extractedText[match.start()-40:match.end()+40]
                if len(subText) == 0:
                    subText = extractedText[match.start()-10:match.end()+40]
                byText[jnumid].append(subText)

allGenes = {}
results = db.sql('''
select ra._refs_key, a1.accid as markerID, a2.accid as jnumID
    from mgi_reference_assoc ra, acc_accession a1, acc_accession a2
    where ra._refassoctype_key = 1018
    and ra._object_key = a1._object_key
    and a1._mgitype_key = 2
    and a1._logicaldb_key = 1
    and a1.preferred = 1
    and a1.prefixPart = 'MGI:'
    and ra._refs_key = a2._object_key
    and a2._mgitype_key = 1
    and a2._logicaldb_key = 1
    and a2.preferred = 1
    and a2.prefixPart = 'J:'
    order by ra._refs_key, a1.accid
    ''', 'auto')
for r in results:
    key = r['jnumID']
    if key not in allGenes:
        allGenes[key] = []
    allGenes[key].append(r['markerID'])

#
# process group/status
#
sql = '''
select r._Refs_key, r.jnumid, concat(g.abbreviation||'|'||s.term) as groupstatus
from extractedText r, BIB_Workflow_Status wfs, VOC_Term g, VOC_Term s
where r._Refs_key = wfs._Refs_key
and wfs._Group_key = g._Term_key
and wfs._Status_key = s._Term_key
and wfs.isCurrent = 1
order by groupstatus
'''
results = db.sql(sql, 'auto')

for r in results:

        jnumid = r['jnumid']
        groupstatus = r['groupstatus']

        if jnumid not in byStatus:
            byStatus[jnumid] = []
        if groupstatus not in byStatus[jnumid]:
            byStatus[jnumid].append(groupstatus)

#
# print report
#
counter = 0
keys = list(byStatus.keys())
keys.sort()
for r in keys:
        geneIds = ''
        if r in allGenes:
            geneIds = '|'.join(allGenes[r])
        if len(byText[r]) > 0:
            fp.write(r + TAB)
            fp.write(byDate[r][0] + TAB)
            fp.write('\t'.join(byStatus[r]) + TAB)
            fp.write('|'.join(byText[r]) + TAB)
            fp.write(geneIds + CRT)
            counter += 1

fp.write('\n(%d rows affected)\n' % counter)
reportlib.finish_nonps(fp)
