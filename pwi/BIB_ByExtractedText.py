
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

import cgi
form = cgi.FieldStorage()
textArg = form["text"].value          if "text" in form else ""
dateArg = form["creation-date"].value if "creation-date" in form else ""
relArg = form["mgi-relevance"].value  if "mgi-relevance" in form else ""

CRT = reportlib.CRT
TAB = reportlib.TAB


sys.stdout.write('pubmedID\tmgiID' + CRT)

# batch this query by batchSize so CGI does not timeout
batchSize = 10000
results = db.sql('select max(_refs_key) as maxKey from BIB_Workflow_Data', 'auto')
maxKey = results[0]['maxKey']
numBatches = int((maxKey / batchSize) + 1)

for i in range(numBatches):

        startKey = i * batchSize
        endKey = startKey + batchSize

        relClause = ""
        if relArg != "all":
            relClause = f"\n\tand r.relevanceterm = '{relArg}'"

        dateClause = ""
        if dateArg:
            dateClause = f"\n\tand br.creation_date >= '{dateArg}'"

        q = '''
        with refkeys as (
            select br._refs_key
            from bib_refs br, BIB_Citation_Cache r
            where br._refs_key = r._refs_key
            and br._refs_key >= %d 
            and br._refs_key <= %d
            --
            %s
            %s
        )
        select r.pubmedID , r.mgiid
        from BIB_Citation_Cache r, BIB_Workflow_Data d, BIB_Refs br, refkeys rk
        where r._refs_key = rk._refs_key
        and r._refs_key = d._refs_key 
        and r._refs_key = br._refs_key
        and d._ExtractedText_key not in (48804491) 
        and lower(d.extractedText) like lower('%s')
        ''' % (startKey, endKey, dateClause, relClause, f'%{textArg}%')

        first = True
        for r in db.sql(q, 'auto'):
                if first:
                    sys.stderr.write(q + '\n')
                    sys.stderr.flush()
                    first = False
                pmid = r['pubmedID'] if r['pubmedID'] else ''
                mgiid = r['mgiID']
                sys.stdout.write(f'{pmid}\t{mgiid}\n')
                sys.stdout.flush()

sys.stdout.flush()

