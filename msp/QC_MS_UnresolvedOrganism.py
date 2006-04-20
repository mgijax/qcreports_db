#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of Unresolved Organisms
#       from QC_MS_UnresolvedOrganism.
#
# Usage:
#       QC_MS_UnresolvedOrganism.py
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

outputDir = os.environ['OUTPUTDIR']
jobStreamKey = os.environ['JOBSTREAM']

radarDB = os.environ['RADAR_DBNAME']
server = os.environ['RADAR_DBSERVER']
db.set_sqlServer(server)
db.set_sqlDatabase(radarDB)

fp = reportlib.init(sys.argv[0],  
		    'Molecular Source Processer - Unresolved Organisms (Job Stream %s)' % (jobStreamKey), 
		    outputdir = outputDir, sqlLogging = 0)

fp.write("  A row in this report represents a Sequence whose Organism could not be resolved to a valid MGI Organism.\n" + 2*CRT)

fp.write(string.ljust('Sequence Acc ID', 30))
fp.write(string.ljust('Organism', 100) + CRT)
fp.write(string.ljust('---------------', 30))
fp.write(string.ljust('--------', 100) + CRT)

#
# select all records for given job stream which do not exists for another job stream
#

results = db.sql('select qc1.accID, qc1.rawOrganism ' + \
	   'from QC_MS_UnresolvedOrganism qc1 ' + \
           'where qc1._JobStream_key = %s ' % (jobStreamKey) + \
	   'and not exists (select 1 from QC_MS_UnresolvedOrganism qc2 ' + \
	   'where qc1.accID = qc2.accID ' + \
	   'and qc1.rawOrganism = qc2.rawOrganism ' + \
	   'and qc1._JobStream_key != qc2._JobStream_key) ' + \
	   ' order by qc1.accID', 'auto')

rows = 0
for r in results:
    fp.write(string.ljust(r['accID'], 30) + \
	     string.ljust(r['rawOrganism'], 25) + CRT)
    rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

