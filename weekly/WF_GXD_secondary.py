
'''
#
# TR12250/Lit Triage
#
# Report:
#
# Usage:
#       WF_GXD_secondary.py
#
#       Group = GXD : removed 12/07
#       Status = Routed
#       
#       Section 1 : removed 12/07
#       Relevance = keep
#
#       Section 2 : removed 12/07
#       Relevanve = discard
#
#       Section 3
#       <=500 characters in body extracted text
#
#       In each section:
#       mgiid
#       pubmedid
#       Relevance Confidence score
#       Count of embryo (exclude references)e.  
#       Count of ignore phrases (exclude references)5.  
#       Exclude any records with tags 'GXD:jf', 'GXD:cms', 'GXD:ijm', 'GXD:jx', 'GXD:th'
#       List the ‘ignore’ phrases at the top of the page
#       Sort by MGI ID descending
#
# History:
#
# 01/22/2021    lec
#       - TR13349/Genome Build 39 project
#	- TR12717/GXD secondary screening
#
'''
 
import sys 
import os 
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

#
# gxd workflow status = Not Routed
# extractedText (body) <= 500 characters
# relevance = Keep, Discard
# reference type = Peer Reviewed Article
# confidence >= -2.75
#
fp.write('\n<=500 characters in body extracted text\n')
fp.write('MGI ID, pmid, Relevance, Confidance\n')
results = db.sql('''
select c.mgiid, c.pubmedid, c.relevanceterm, v.confidence
from bib_citation_cache c, bib_workflow_relevance v
where c.relevanceterm in ('keep', 'discard')
and c.referencetype = 'Peer Reviewed Article'
and c._refs_key = v._refs_key
and v.isCurrent = 1
and v.confidence >= -2.75
and exists (select 1 from bib_workflow_status s 
        where c._refs_key = s._refs_key
        and s.isCurrent = 1
        and s._group_key = 31576665
        and s._status_key = 31576669
        )
and exists (select 1 from bib_workflow_data d 
        where c._refs_key = d._refs_key
        and d._extractedtext_key = 48804490
        and char_length(d.extractedText) <= 500
        )
order by c.mgiid
''', 'auto')
for r in results:
        fp.write(r['mgiid'] + TAB)
        fp.write(str(r['pubmedid']) + TAB)
        fp.write(r['relevanceterm'] + TAB)
        fp.write(str(r['confidence']) + CRT)

fp.write('\n(%d rows affected)\n' % len(results))

reportlib.finish_nonps(fp)

