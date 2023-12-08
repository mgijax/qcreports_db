
'''
#
# WTS2-682
#
# Report:
#       Produce a tab-delimited report with the following output fields:
#
#       COV tag name
#       Count of references associated with the tag
#
# Usage:
#       BIB_COVRefTagCounts.py
#
# History:
#
# dbm   10/7/2019
#       - created
#
'''
 
import sys 
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

fp.write('Tag' + TAB + 'Reference Count' + CRT)

cmd = '''
        select t.term, count(*) as ref_count
        from voc_term t, bib_workflow_tag r
        where t._vocab_key = 129 and
              t.term ilike 'cov:%' and
              t._term_key = r._tag_key
        group by t.term
        order by t.term
        '''

results = db.sql(cmd, 'auto')

for r in results:
    fp.write(r['term'] + TAB + str(r['ref_count']) + CRT)

reportlib.finish_nonps(fp)
