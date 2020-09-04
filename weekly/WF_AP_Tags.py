
'''
#
# Report:
#
# Notes:
#
# History:
#
# 09/04/2020    lec
#	- TR13327
#       1) References tagged with AP:New_allele_new_gene
#       2) References tagged with AP:NewAlleleNomenclature
#       3) References tagged with AP:NewDiseaseModel
#       4) References tagged with AP:NewRecombinase
#
#       J number
#       PMID
#       Publication year
#       AP reference status (i.e. routed, chosen, indexed, etc)
#       All AP or MGI:curator reference tags (pipe delimited)
#       text of reference note  (leave blank if null)
#
#       sort all by 
#       1) publication year, oldest to newest
#       2) J number, lowest to highest
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

fp = reportlib.init(sys.argv[0], 'AP tagged references for curation', os.environ['QCOUTPUTDIR'], printHeading = None)

results = db.sql('''
select r._Refs_key, c.numericpart, c.jnumid, c.pubmedid, r.year, wftag._tag_key, tt.term as tagterm, st.term as statusterm
into temp table refs
from BIB_Refs r, BIB_Citation_Cache c, 
BIB_Workflow_Tag wftag, VOC_Term tt,
BIB_Workflow_Status wfstatus, VOC_Term st
where r.isDiscard = 0
and r._Refs_key = c._Refs_key
and r._Refs_key = wftag._Refs_key
and wftag._Tag_key in (35710200, 31576700, 31576701, 31576709)
and wftag._Tag_key = tt._Term_key
and r._Refs_key = wfstatus._Refs_key
and wfstatus._group_key = 31576664
and wfstatus.isCurrent = 1
and wfstatus._Status_key = st._Term_key
order by wftag._tag_key, r.year, c.numericpart
''', None)

db.sql('create index idx_refs on refs(_Refs_key)', None)

allTags = {}
results = db.sql('''
select distinct r._refs_key, tt.term
from refs r, BIB_Workflow_Tag wftag, VOC_Term tt
where r._Refs_key = wftag._Refs_key
and wftag._Tag_key = tt._Term_key
and (tt.term like 'AP:%' or tt.term like 'MGI:curator%')
''', 'auto')
for r in results:
        key = r['_Refs_key']
        value = r['term']
        if key not in allTags:
                allTags[key] = []
        allTags[key].append(value)
#print(allTags)

allNotes = {}
results = db.sql('''
select distinct r._refs_key, n.note
from refs r, BIB_Notes n
where r._Refs_key = n._Refs_key
''', 'auto')
for r in results:
        key = r['_Refs_key']
        value = ''.join(c for c in r['note'] if ord(c) >= 32)
        if key not in allNotes:
                allNotes[key] = []
        allNotes[key].append(value)
#print(allNotes)

results = db.sql('select * from refs', 'auto')
for r in results:
        key = r['_Refs_key']
        fp.write(r['tagTerm'] + TAB)
        fp.write(r['jnumid'] + TAB)
        fp.write(str(r['pubmedid']) + TAB)
        fp.write(str(r['year']) + TAB)
        fp.write(r['statusterm'] + TAB)
        if key in allTags:
                fp.write('|'.join(allTags[key]))
        fp.write(TAB)
        if key in allNotes:
                fp.write('|'.join(allNotes[key]))
        fp.write(CRT)

reportlib.finish_nonps(fp)
