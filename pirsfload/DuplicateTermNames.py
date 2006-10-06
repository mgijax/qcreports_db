#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of PIRSF superfamily ids 
#       loaded into MGD with duplicates names
#
# Usage:
#       "DuplicateTermNames.py
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
import pdb

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#
#pdb.set_trace()
outputDir=sys.argv[1]
server=sys.argv[2]
mgdDB=sys.argv[3]
radarDB=sys.argv[4]
jobKey=sys.argv[5]

db.set_sqlServer(server)
db.set_sqlDatabase(mgdDB)
db.useOneConnection(1)

cmds = []

cmds = "select v.term " + \
   "into #WRK_dupterms " + \
   "from VOC_Term v, ACC_Accession a " + \
   "where v._Vocab_key = 49 " + \
   "and a._Object_key = v._Term_key " + \
   "and a._LogicalDB_key = 78 " + \
   "group by v.term " + \
   "having count(a.accid) > 1"

results = db.sql(cmds, 'auto')

cmds = "select v.term, a.accID " + \
   "from VOC_Term v, #WRK_dupterms d, ACC_Accession a " + \
   "where v.term = d.term " + \
   "and v._Term_key = a ._Object_key " + \
   "and a._LogicalDB_key = 78 " + \
   "order by v.term"

results = db.sql(cmds, 'auto')

fp = reportlib.init(sys.argv[0],  
		    'PIRSFLoad - Duplicate terms loaded into MGD (Job Stream %s)' % (jobKey), 
		    outputdir = outputDir, sqlLogging = 0)

fp.write("  A row in this report represents a superfamily term and id\n" + \
"  where the term is used in more than one superfamilies." + 2*CRT)

fp.write(string.ljust('Term name', 100))
fp.write(string.ljust('Superfamily ID', 15))
fp.write(CRT)
fp.write(string.ljust('------------------------------------------------------------------------------------------', 100))
fp.write(string.ljust('---------------', 15))
fp.write(CRT)

rows = 0
for r in results:
    fp.write(string.ljust(r['term'], 100) + \
             string.ljust(r['accid'], 15) + \
	     CRT)
    rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))

reportlib.finish_nonps(fp)

