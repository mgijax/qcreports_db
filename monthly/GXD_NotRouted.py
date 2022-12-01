'''
#
# Papers used by GXD that were Not Routed
#
# Usage:
#       GXD_NotRouted.py
#
# Query:
#       GXD status = Not Routed where isCurrent = 0
#       GXD status = Chosen, Indexed, Full Coded where isCurrent = 1
#       may contain Tag that begins 'GXD'
#
# Output:
#       jnum, descending
#       GXD status
#       Tag
#
# History:
#
# lec   12/01/2022
#       fl2-55/gxd secondary triage
#
'''
 
import sys
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

fp = reportlib.init(sys.argv[0], 'Papers used by GXD that were Not Routed', os.environ['QCOUTPUTDIR'])

results = db.sql('''
WITH refs AS (
select c._refs_key, c.jnumid, t1.term as statusTerm, v.confidence
from bib_citation_cache c, bib_workflow_status s1, voc_term t1, bib_workflow_relevance v
where c.jnumid is not null
and c._refs_key = s1._refs_key
and s1.isCurrent = 1
and s1._group_key = 31576665
and s1._status_key in (31576671, 31576673, 31576674)
and s1._status_key = t1._term_key
and c._refs_key = v._refs_key
and v._modifiedby_key = 1617
and exists (select 1 from bib_workflow_status s0 where c._refs_key = s0._refs_key
        and s0.isCurrent = 0
        and s0._group_key = 31576665
        and s0._status_key = 31576669   -- Not Routed
        )
)
(
select r.*, t.term as tagTerm
from refs r, bib_workflow_tag g, voc_term t
where r._refs_key = g._refs_key
and g._tag_key = t._term_key
and t.term like 'GXD%'
union
select r.*, null
from refs r
where not exists (select 1 from bib_workflow_tag g, voc_term t
        where r._refs_key = g._refs_key
        and g._tag_key = t._term_key
        and t.term like 'GXD%'
        )
)
order by jnumid desc, statusTerm
''', 'auto')

for r in results:
        fp.write(r['jnumid'] + TAB)

        if r['confidence'] == None:
                fp.write(TAB)
        else:
                fp.write(str(r['confidence']) + TAB)

        fp.write(r['statusTerm'] + TAB)

        if r['tagTerm'] == None:
                fp.write(CRT)
        else:
                fp.write(r['tagTerm'] + CRT)

reportlib.finish_nonps(fp)
