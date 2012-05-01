#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of Merged Sequences from QC_SEQ_Merged.
#
# Usage:
#       QC_MS_Merged.py OutputDir JobKey MGDDBinstance
#
# Notes:
#
# History:
#
# lec   03/30/2004
#       - created
#
'''
 
import sys 
import os
import string
import reportlib

try:
    if os.environ['DB_TYPE'] == 'postgres':
        import pg_db
        db = pg_db
        db.setTrace()
        db.setAutoTranslateBE()
    else:
        import db
except:
    import db


CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

outputDir = sys.argv[1]
jobStreamKey = sys.argv[2]

mgdDB = os.environ['MGD_DBNAME']
radarDB = os.environ['RADAR_DBNAME']
server = os.environ['RADAR_DBSERVER']
db.set_sqlServer(server)
db.set_sqlDatabase(radarDB)

#
# Main
#

fp = reportlib.init(sys.argv[0],  
		    'Sequence Loader - Merged Sequences (Job Stream %s)' % (jobStreamKey), 
		    outputdir = outputDir, sqlLogging = 0)

fp.write("  A row in this report represents a Sequence that is designated as Merged\n" + \
"  by the Sequence provider." + 2*CRT)

fp.write(string.ljust('From Sequence ID', 35))
fp.write(string.ljust('To Sequence ID', 35))
fp.write(CRT)
fp.write(string.ljust('----------------', 35))
fp.write(string.ljust('--------------', 35))
fp.write(CRT)

results = db.sql('select qc.fromSeqId, qc.toSeqId ' + \
	    'from QC_SEQ_Merged qc ' + \
            'where qc._JobStream_key = %s ' % (jobStreamKey) + \
	    'order by fromSeqId', 'auto')

rows = 0
for r in results:
    fp.write(string.ljust(r['fromSeqId'], 35) + \
             string.ljust(r['toSeqId'], 35) + \
	     CRT)
    rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))

reportlib.finish_nonps(fp)

