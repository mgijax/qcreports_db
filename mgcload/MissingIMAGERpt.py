#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of input records that have missing
#       IMAGE IDs.
#
#       The report contains the following tab-delimited fields:
#
#       1) MGC ID (if it is not null)
#       2) Sequence ID (if it is not null)
#
#       This report assumes that the MGC load has been run and the data for
#       the report has been populated in the QC_MGCLoad_IMAGE_Missing
#       table in the RADAR database.
#
# Usage:
#       MissingIMAGERpt.py  OutputDir  Server  RADAR  JobKey
#
# Notes:
#
# History:
#
# dbm   12/22/2004
#       - new
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
 
fp = reportlib.init(outputfile='MissingIMAGE.rpt', outputdir=outputDir,
                    printHeading = None, sqlLogging = 0)

db.set_sqlServer(server)
db.set_sqlDatabase(radarDB)

cmd = []
cmd.append('select d.mgcID, d.seqID ' + \
           'from DP_MGC_Clones d ' + \
           'where exists (select 1 ' + \
                         'from QC_MGCLoad_IMAGE_Missing q ' + \
                         'where q._MGCClone_key = d._MGCClone_key and ' + \
                               'q._JobStream_key = ' + jobKey + ') ' + \
           'order by d.mgcID, d.seqID')

results = db.sql(cmd, 'auto')

for r in results[0]:
    mgcID = r['mgcID']
    seqID = r['seqID']
    if (mgcID == None):
        mgcID = ""
    if (seqID == None):
        seqID = ""
    fp.write(mgcID + TAB + seqID + CRT)

reportlib.finish_nonps(fp)
