#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of clones that have more than one
#       resolved library name.
#
#       The report contains the following tab-delimited fields:
#
#       1) Unique clone number to identify records belonging to the same clone
#       2) 1 or more sequence IDs (comma separated if more than one)
#       3) Resolved clone library name
#       4) 1 or more clone IDs (comma separated if more than one)
#
#       This report assumes that the GenBank EST cDNA clone load has been
#       run and the data for the report has been populated in the
#       QC_cDNALoad_Library_Discrep table in the RADAR database.
#
# Usage:
#       LibraryDiscrepancy.py  OutputDir  Server  RADAR  JobKey
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
 
fp = reportlib.init(outputfile='LibraryDiscrepancy.rpt', outputdir=outputDir,
                    printHeading = 0)
db.set_sqlServer(server)
db.set_sqlDatabase(radarDB)

cmd = []
cmd.append('select distinct w.cloneNum, w.accID, w.logicalDB, ' + \
                  'w.primarySeqID, l.goodName ' + \
           'from WRK_cDNA_Clones w, MGI_CloneLibrary l ' + \
           'where w.libraryNum = l.libraryNum and ' + \
                 'exists (select 1 ' + \
                         'from QC_cDNALoad_Library_Discrep q ' + \
                         'where q.cloneNum = w.cloneNum and ' + \
                               'q._JobStream_key = ' + jobKey + ') and ' + \
                 'w.original = 1 ' + \
           'order by w.cloneNum, w.primarySeqID')

results = db.sql(cmd, 'auto')

oldCloneNum = 0
oldPrimarySeqID = ""

seqIDs = ""
cloneIDs = ""
library = ""

for r in results[0]:
    cloneNum = r['cloneNum']
    accID = r['accID']
    logicalDB = r['logicalDB']
    primarySeqID = r['primarySeqID']
    goodName = r['goodName']

    if (cloneNum != oldCloneNum or primarySeqID != oldPrimarySeqID):
        if (oldCloneNum != 0):
            fp.write(str(oldCloneNum) + TAB + seqIDs + TAB + \
                     library + TAB + cloneIDs + CRT)
        oldCloneNum = cloneNum
        oldPrimarySeqID = primarySeqID
        seqIDs = ""
        cloneIDs = ""
        library = ""

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

    library = goodName

if (oldCloneNum != 0):
    fp.write(str(oldCloneNum) + TAB + seqIDs + TAB + library + TAB + \
             cloneIDs + CRT)

reportlib.finish_nonps(fp)
