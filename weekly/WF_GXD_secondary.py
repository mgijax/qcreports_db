
'''
#
# TR12250/Lit Triage
#
# Report:
#
# Usage:
#       WF_GXD_secondary.py
#
#       Group = GXD
#       Status = Routed
#       
#       Section 1
#       Relevance = keep
#
#       Section 2
#       Relevanve = discard
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
import re
import reportlib
import db

#db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

searchTerms = [
'embryo',
]

excludedTerms = ''
sql = ''
extractedSql = ''

def process(sql):

        # general processing
        results = db.sql(sql, 'auto')

        # iterate thru each distinct reference
        for r in results:

                totalMatchesTerm = 0
                totalMatchesExcludedTerm = 0

                eresults = db.sql(extractedSql % (r['_refs_key']), 'auto')
                for e in eresults:
                    matchesExcludedTerm = 0
                    extractedText = e['extractedText']
                    extractedText = extractedText.replace('\n', ' ')
                    extractedText = extractedText.replace('\r', ' ')

                    for s in searchTerms:
                        for match in re.finditer(s, extractedText):
                            subText = extractedText[match.start()-50:match.end()+50]
                            if len(subText) == 0:
                                subText = extractedText[match.start()-50:match.end()+50]

                            matchesExcludedTerm = 0
                            for e in excludedTerms:
                                for match2 in re.finditer(e, subText):
                                    matchesExcludedTerm = 1

                            # if subText matches excluded term
                            if matchesExcludedTerm == 0:
                                fp.write(subText + '\n')
                                totalMatchesTerm += 1
                            else:
                                totalMatchesExcludedTerm += 1
                                                
                fp.write(r['mgiid'] + TAB)
                fp.write(str(r['pubmedid']) + TAB)
                fp.write(str(r['confidence']) + TAB)
                fp.write(str(totalMatchesTerm) + TAB)
                fp.write(str(totalMatchesExcludedTerm) + CRT*2)

        fp.write('\n(%d rows affected)\n' % len(results))

#
#  MAIN
#

# distinct references
# where relevance = '?'
#       status = 'Routed'
#       non-reference extracted text exists
sql = '''
select distinct c._refs_key, c.mgiid, c.pubmedid, s._group_key, v.confidence
from bib_citation_cache c, bib_refs r, bib_workflow_relevance v, bib_workflow_status s
where r._refs_key = c._refs_key
and r._refs_key = v._refs_key
and v.isCurrent = 1
and v._relevance_key = %s
and r._refs_key = s._refs_key
and s._status_key = 31576670
and s._group_key = 31576665
and s.isCurrent = 1
and exists (select 1 from bib_workflow_data d
    where r._refs_key = d._refs_key
    and d._extractedtext_key not in (48804491)
    and d.extractedText is not null
    )
and not exists (select 1 from bib_workflow_tag t
    where r._refs_key = t._refs_key
    and t._tag_key in (34447095,36021716,34447096,34447098,34447097)
    )
order by mgiid desc
'''

# extracted_text by _refs_key where extracted text type != 'reference'
extractedSql = '''
    select lower(d.extractedText) as extractedText
    from bib_workflow_data d
    where d._refs_key = %s
    and d._extractedtext_key not in (48804491)
    and d.extractedText is not null
'''

excludedTerms = []
results = db.sql('select lower(term) as term from voc_term where _vocab_key = 135 order by term', 'auto')
for r in results:
    excludedTerms.append(r['term'])
#print(excludedTerms)

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])
fp.write('\nset of "Lit Triage GXD ignore extracted text" (_vocab_key = 135):\n')
fp.write('\n'.join(excludedTerms) + '\n\n')

fp.write('\nkeep\n')
process(sql % (70594667))

fp.write('\ndiscard\n')
process(sql % (70594666))

reportlib.finish_nonps(fp)

