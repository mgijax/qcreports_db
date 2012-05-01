#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of PIRSF superfamily ids 
#       loaded into MGD with duplicates names
#
# Usage:
#       DuplicateTermNames.py
#
# Notes:
#
# History:
#
# mbw   10/03/2005
#       - created
#
'''
 
import os
import sys 
import db
import string
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#
outputDir=sys.argv[1]
jobKey=sys.argv[2]

fp = reportlib.init(sys.argv[0],  'PIRSFLoad - Duplicate terms loaded into MGD (Job Stream %s)' % (jobKey), outputdir = outputDir, sqlLogging = 0)

fp.write('\tA row in this report represents a superfamily term that is used in more than one superfamily.\n\n')
fp.write(string.ljust('Term name', 100))
fp.write(string.ljust('Superfamily ID', 15))
fp.write(CRT)
fp.write(string.ljust('------------------------------------------------------------------------------------------', 100))
fp.write(string.ljust('---------------', 15))
fp.write(CRT)

db.sql('''
	select v._Term_key, v.term 
   	into #dupterms 
   	from VOC_Term v 
   	where v._Vocab_key = 46 
   	group by v.term having count(*) > 1
	''', None)

db.sql('create index idx1 on #dupterms(_Term_key)', None)

results = db.sql('''
	select d.term, a.accID 
   	from #dupterms d, ACC_Accession a 
   	where d._Term_key = a ._Object_key 
   	and a._LogicalDB_key = 78 
   	order by d.term
	''', 'auto')

for r in results:
    fp.write(string.ljust(r['term'], 100) + \
             string.ljust(r['accID'], 15) + \
	     CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)
