
'''
#
# Lit Triage : Search Extracted Text
#
# Search Extracted Text : body + start methods + supplemental data + author manuscript fig legends. 
# Exclude references. 
#
# Note: extracted text is pre-supplementary data 
#       <A HREF="http://www.theasciicode.com.ar/extended-ascii-code/degree-symbol-ascii-code-248.html">http://www.theasciicode.com.ar/extended-ascii-code/degree-symbol-ascii-code-248.html</A>
#
'''
 
import sys
import os
import db
import reportlib

#db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

value = '%' + sys.argv[1] + '%'

results = db.sql('''
select r.pubmedID 
from BIB_Citation_Cache r, BIB_Workflow_Data d 
where r.pubmedid is not null
and r._Refs_key = d._Refs_key 
and d._ExtractedText_key not in (48804491) 
and lower(d.extractedText) like lower('%s')
''' % (value), 'auto')

sys.stdout.write('pubmedID' + CRT)

for r in results:
        sys.stdout.write(r['pubmedID'] + CRT)

sys.stdout.flush()

