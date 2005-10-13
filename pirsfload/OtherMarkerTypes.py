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

cmds = "select mt.name, acc1.accid as 'markerid', m.symbol, acc2.accid as 'sfid', t.term " + \
       "from mrk_marker m, mrk_types mt, acc_accession acc1, acc_accession acc2, voc_annot a, voc_term t " + \
       "where a._annottype_key = 1007 " + \
       "and acc1._object_key = a._object_key " + \
       "and acc1._mgitype_key = 2 " + \
       "and acc1._logicaldb_key = 1 " + \
       "and acc1.preferred = 1 " + \
       "and m._marker_key = a._object_key " + \
       "and mt._marker_type_key = m._marker_type_key " + \
       "and m._marker_type_key != 1 " + \
       "and acc2._object_key = a._term_key " + \
       "and acc2._mgitype_key = 13 " + \
       "and t._term_key = a._term_key " + \
       "order by name"

results = db.sql(cmds, 'auto')

fp = reportlib.init(sys.argv[0],  
		    'PIRSFLoad - Annotations loaded into MGD to markers other than genes (Job Stream %s)' % (jobKey), 
		    outputdir = outputDir, sqlLogging = 0)

fp.write("  A row in this report represents an annotation to a marker of type other than gene." + 2*CRT)

fp.write(string.ljust('Marker type', 30))
fp.write(string.ljust('MGI Marker ID', 20))
fp.write(string.ljust('Symbol', 20))
fp.write(string.ljust('Superfamily ID', 15))
fp.write(string.ljust('Superfamily Name', 80))
fp.write(CRT)
fp.write(string.ljust('-----------------------------', 30))
fp.write(string.ljust('-------------------', 20))
fp.write(string.ljust('-------------------', 20))
fp.write(string.ljust('--------------', 15))
fp.write(string.ljust('-------------------------------------------------------------------------------', 80))
fp.write(CRT)

rows = 0
for r in results:
    fp.write(string.ljust(r['name'], 30) + \
             string.ljust(r['markerid'], 20) + \
             string.ljust(r['symbol'], 20) + \
             string.ljust(r['sfid'], 15) + \
             string.ljust(r['term'], 80) + \
	     CRT)
    rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

