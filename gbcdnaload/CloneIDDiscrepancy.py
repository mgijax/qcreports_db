#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of clones that have more than one
#       clone ID with the same logical DB.
#
#       The report contains the following tab-delimited fields:
#
#       1) Unique clone number to identify records belonging to the same clone
#       2) 1 or more sequence IDs (comma separated if more than one)
#       3) 2 or more clone IDs (comma separated if more than one)
#
#       This report assumes that the GenBank EST cDNA clone load has been
#       run and the data for the report has been populated in the
#       QC_cDNALoad_CloneID_Discrep table in the RADAR database.
#
# Usage:
#       CloneIDDiscrepancy.py  OutputDir  Server  RADAR  JobKey
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
 
fp = reportlib.init(outputfile='CloneIDDiscrepancy.rpt', outputdir=outputDir,
                    printHeading = 0, sqlLogging = 0)

db.set_sqlServer(server)
db.set_sqlDatabase(radarDB)

cmd = []
cmd.append('select w.cloneNum, w.accID, w.logicalDB, w.primarySeqID ' + \
           'from WRK_cDNA_Clones w ' + \
           'where exists (select 1 ' + \
                         'from QC_cDNALoad_CloneID_Discrep q ' + \
                         'where q.cloneNum = w.cloneNum and ' + \
                               'q._JobStream_key = ' + jobKey + ') and ' + \
                 'w.original = 1 ' + \
           'order by w.cloneNum, w.primarySeqID')

results = db.sql(cmd, 'auto')

oldCloneNum = 0
oldPrimarySeqID = ""

seqIDs = ""
cloneIDs = ""

for r in results[0]:
    cloneNum = r['cloneNum']
    accID = r['accID']
    logicalDB = r['logicalDB']
    primarySeqID = r['primarySeqID']

    if (cloneNum != oldCloneNum or primarySeqID != oldPrimarySeqID):
        if (oldCloneNum != 0):
            fp.write(str(oldCloneNum) + TAB + seqIDs + TAB + \
                     cloneIDs + CRT)
        oldCloneNum = cloneNum
        oldPrimarySeqID = primarySeqID
        seqIDs = ""
        cloneIDs = ""

    if (logicalDB == "Sequence DB"):
        if (seqIDs == ""):
            seqIDs = accID
        else:
            seqIDs = seqIDs + "," + accID

    else:
        if (cloneIDs == ""):
            cloneIDs = accID
        else:
            cloneIDs = cloneIDs + "," + accID

if (oldCloneNum != 0):
    fp.write(str(oldCloneNum) + TAB + seqIDs + TAB + cloneIDs + CRT)

reportlib.finish_nonps(fp)
