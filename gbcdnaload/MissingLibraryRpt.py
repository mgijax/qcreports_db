#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of input records that are missing
#       the expected resolved clone library based on the clone IDs.
#
#       The report contains the following tab-delimited fields:
#
#       1) 1 or more sequence IDs (comma separated if more than one)
#       2) Raw clone library name
#       3) 1 or more clone IDs (comma separated if more than one)
#       4) 0 or more MGI IDs (comma separated if more than one)
#
#       This report assumes that the GenBank EST cDNA clone load has been
#       run and the data for the report has been populated in the
#       QC_cDNALoad_Library_Missing table in the RADAR database.
#
# Usage:
#       MissingLibraryRpt.py  OutputDir  Server  RADAR  JobKey
#
# Notes:
#
# History:
#
# dbm   06/04/2004
#       - created
#
'''
 
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
server=sys.argv[2]
radarDB=sys.argv[3]
jobKey=sys.argv[4]

fp = reportlib.init(outputfile='MissingLibrary.rpt', outputdir=outputDir,
                    printHeading = 0)

db.set_sqlServer(server)
db.set_sqlDatabase(radarDB)

cmd = []
cmd.append('select seqIDList, rawLibrary, cloneIDList, mgiIDList ' + \
           'from QC_cDNALoad_Library_Missing ' + \
           'where _JobStream_key = ' + jobKey + ' ' + \
           'order by _QCRecord_key')

results = db.sql(cmd, 'auto')

for r in results[0]:
    mgiIDList = r['mgiIDList']
    if (mgiIDList == None):
        mgiIDList = ""
    fp.write(r['seqIDList'] + TAB + r['rawLibrary'] + TAB + \
             r['cloneIDList'] + TAB + mgiIDList + CRT)

reportlib.finish_nonps(fp)
