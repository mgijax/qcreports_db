#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of Invalid Libraries
#       from QC_MS_InvalidLibrary.
#
# Usage:
#       QC_MS_InvalidLibrary.py
#
# Notes:
#
# History:
#
# lec   03/16/2004
#       - created
#
'''
 
import os
import sys 
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

outputDir = os.environ['OUTPUTDIR']
jobStreamKey = os.environ['JOBSTREAM']

radarDB = os.environ['RADAR_DBNAME']
server = os.environ['RADAR_DBSERVER']
db.set_sqlServer(server)
db.set_sqlDatabase(radarDB)

fp = reportlib.init(sys.argv[0],  
		    'Molecular Source Processer - Invalid Libraries (Job Stream %s)' % (jobStreamKey), 
		    outputdir = outputDir, sqlLogging = 0)

fp.write("  A row in this report represents a Library that could not be translated to a valid MGI Library.\n" + \
"  This Library may need to be added to the Library bad name/good name list.\n" + 2*CRT)

fp.write(string.ljust('Library', 100))
fp.write(string.ljust('Number of Occurrences', 25) + CRT)
fp.write(string.ljust('-------', 100))
fp.write(string.ljust('---------------------', 25) + CRT)

#
# select all libraries for given job stream which do not appear within another job stream
#

results = db.sql('select qc1.library, qc1.numberOfOccurrences ' + \
	   'from QC_MS_InvalidLibrary qc1 ' + \
           'where qc1._JobStream_key = %s ' % (jobStreamKey) + \
	   'and not exists (select 1 from QC_MS_InvalidLibrary qc2 ' + \
	   'where qc1.library = qc2.library ' + \
	   'and qc1._JobStream_key != qc2._JobStream_key) ' + \
	   ' order by qc1.numberOfOccurrences desc, qc1.library', 'auto')

rows = 0
for r in results:
    fp.write(string.ljust(r['library'], 100) + \
	     string.ljust(str(r['numberOfOccurrences']), 25) + CRT)
    rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))

reportlib.finish_nonps(fp)

