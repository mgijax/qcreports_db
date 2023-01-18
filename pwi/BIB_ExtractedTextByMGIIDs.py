
'''
#
# Extracted Text in database - Search by ID
#
'''
 
import sys
import os
import db
import reportlib

#db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

value = list(sys.argv[1].split(' '))
value = "'" + "','".join(value) + "'"

sys.stdout.write('MGI ID' + TAB)
sys.stdout.write('J#' + TAB)
sys.stdout.write('pmid' + TAB)
sys.stdout.write('creation date' + TAB)
sys.stdout.write('section label' + TAB)
sys.stdout.write('extracted text' + TAB)
sys.stdout.write('count of characters in section' + CRT)

results = db.sql('''
select c.mgiid, c.jnumid, c.pubmedid, t.term, char_length(d.extractedtext) as textcount, d.* 
from BIB_Citation_Cache, BIB_Workflow_Data d, VOC_Term t
where c.mgiid in (%s)
and c._refs_key = d._refs_key
and d._extractedtext_key != 48804491
and d._extractedtext_key = t._term_key
order by c.mgiid, t.term
''' % (value), 'auto')

for i in results:

        sys.stdout.write(r['mgiid'] + TAB)

        if r['jnumID'] is None:
                sys.stdout.write(TAB)
        else:
                sys.stdout.write(r['jnumID'] + TAB)

        if r['pubmedID'] is None:
                sys.stdout.write(TAB)
        else:
                sys.stdout.write(r['pubmedID'] + TAB)

        sys.stdout.write(r['creation_date'] + TAB)
        sys.stdout.write(r['term'] + TAB)
        sys.stdout.write(r['extractedtext'] + TAB)
        sys.stdout.write(r['textcount'] + TAB)

        sys.stdout.flush()

sys.stdout.flush()

