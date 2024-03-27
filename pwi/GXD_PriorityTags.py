'''
#
# GXD_PriorityTags.py
#
# GXD workflow tags (129)
# where abbreviation like 'To be used for full-coding priorities'
#
# Report lists:
# term
# note/description
#
'''
 
import sys
import os
import db
import reportlib

#db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

results = db.sql('''
select term, note
from VOC_Term 
where _vocab_key = 129
and term like 'GXD%'
and abbreviation like 'To be used for full-coding priorities%'
order by term
''', 'auto')

sys.stdout.write('term' + TAB)
sys.stdout.write('note' + CRT)

for r in results:
        sys.stdout.write(str(r['term']) + TAB)
        sys.stdout.write(str(r['note'] + CRT)

sys.stdout.flush()

