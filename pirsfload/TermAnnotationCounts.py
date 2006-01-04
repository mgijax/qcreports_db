#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of counts of PIRSF superfamily terms 
#       and of counts of marker annotations to PIRSF superfamily terms loaded 
#       into MGD
#
# Usage:
#       "PIRSFTermCounts.py
#
# Notes:
#
# History:
#
# mbw   12/27/2005
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

cmds = "select count(*) as terms from voc_term where _vocab_key = 46"
results1 = db.sql(cmds, 'auto')

cmds = "select count(*) as annotations from voc_annot where _annottype_key = 1007"
results2 = db.sql(cmds, 'auto')

fp = reportlib.init(sys.argv[0],  
		    'PIRSFLoad - Counts of superfamily terms and marker annotations (Job Stream %s)' % (jobKey), 
		    outputdir = outputDir, sqlLogging = 0)

fp.write(string.ljust('Term count', 15))
fp.write(string.ljust('Annotation count', 15))
fp.write(CRT)
fp.write(string.ljust('---------------', 15))
fp.write(string.ljust('---------------', 15))
fp.write(CRT)

r1 = results1[0]
r2 = results2[0]

fp.write(string.ljust(str(r1['terms']), 15) + \
         string.ljust(str(r2['annotations']), 15) + \
    CRT)

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

