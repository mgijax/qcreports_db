#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of clones with the following
#       MGI/IMAGE ID discrepancies:
#
#       1) The clone has an MGI ID and no IMAGE ID, but the MGI ID exists
#          in the IMG_MGI_IMAGE table.
#       2) The clone has an MGI ID and an IMAGE ID, but the IMAGE ID exists
#          in the IMG_MGI_IMAGE table with a different MGI ID.
#       3) The clone has an MGI ID and an IMAGE ID, but the MGI ID exists
#          in the IMG_MGI_IMAGE table with a different IMAGE ID.
#
#       The report contains the following tab-delimited fields:
#
#       1) MGI ID from the clone (may be null)
#       2) IMAGE ID from the clone (may be null)
#       3) MGI ID from the IMG_MGI_IMAGE table
#       4) IMAGE ID from the IMG_MGI_IMAGE table
#       5) 1 or more sequence IDs (comma separated if more than one)
#       6) 1 or more clone IDs (comma separated if more than one)
#       7) 1 or more clone IDs (comma separated if more than one)
#
#       This report assumes that the GenBank EST cDNA clone load has been
#       run and the data for the report has been populated in the
#       QC_cDNALoad_MGI_IMAGE_Discrep table in the RADAR database.
#
# Usage:
#       MGIIMAGEDiscrepancy.py  OutputDir  Server  RADAR  JobKey
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

discrepType = ['Missing IMAGE ID','MGI ID Discrep','IMAGE ID Discrep']

#
# Main
#
outputDir=sys.argv[1]
server=sys.argv[2]
radarDB=sys.argv[3]
jobKey=sys.argv[4]
 
fp = reportlib.init(outputfile='MGIIMAGEDiscrepancy.rpt', outputdir=outputDir,
                    printHeading = 0)
db.set_sqlServer(server)
db.set_sqlDatabase(radarDB)

cmd = []
cmd.append('select 1 "discrepNum", q.cloneNum, ' + \
                  'q.mgiID "qcMGIID", q.imageID "qcIMAGEID", ' + \
                  'i.mgiID "refMGIID", i.imageID "refIMAGEID", ' + \
                  'w.accID, w.logicalDB ' + \
           'from radar_release..QC_cDNALoad_MGI_IMAGE_Discrep q, ' + \
                'radar_release..IMG_MGI_IMAGE i, ' + \
                'radar_release..WRK_cDNA_Clones w ' + \
           'where q.mgiID = i.mgiID and ' + \
                 'q.imageID is null and ' + \
                 'q.cloneNum = w.cloneNum and ' + \
                 'q._JobStream_key = ' + jobKey + ' and ' + \
                 'w.original = 1 ' + \
           'union ' + \
           'select 2 "discrepNum", q.cloneNum, ' + \
                  'q.mgiID "qcMGIID", q.imageID "qcIMAGEID", ' + \
                  'i.mgiID "refMGIID", i.imageID "refIMAGEID", ' + \
                  'w.accID, w.logicalDB ' + \
           'from radar_release..QC_cDNALoad_MGI_IMAGE_Discrep q, ' + \
                'radar_release..IMG_MGI_IMAGE i, ' + \
                'radar_release..WRK_cDNA_Clones w ' + \
           'where q.mgiID <> i.mgiID and ' + \
                 'q.imageID = i.imageID and ' + \
                 'q.cloneNum = w.cloneNum and ' + \
                 'q._JobStream_key = ' + jobKey + ' and ' + \
                 'w.original = 1 ' + \
           'union ' + \
           'select 3 "discrepNum", q.cloneNum, ' + \
                  'q.mgiID "qcMGIID", q.imageID "qcIMAGEID", ' + \
                  'i.mgiID "refMGIID", i.imageID "refIMAGEID", ' + \
                  'w.accID, w.logicalDB ' + \
           'from radar_release..QC_cDNALoad_MGI_IMAGE_Discrep q, ' + \
                'radar_release..IMG_MGI_IMAGE i, ' + \
                'radar_release..WRK_cDNA_Clones w ' + \
           'where q.mgiID = i.mgiID and ' + \
                 'q.imageID <> i.imageID and ' + \
                 'q.cloneNum = w.cloneNum and ' + \
                 'q._JobStream_key = ' + jobKey + ' and ' + \
                 'w.original = 1 ' + \
           'order by discrepNum, q.cloneNum')

results = db.sql(cmd, 'auto')

oldDiscrepNum = 0
oldQCMGIID = ""
oldQCIMAGEID = ""

seqIDs = ""
cloneIDs = ""
mgiIDs = ""

for r in results[0]:
    discrepNum = r['discrepNum']
    qcMGIID = r['qcMGIID']
    qcIMAGEID = r['qcIMAGEID']
    refMGIID = r['refMGIID']
    refIMAGEID = r['refIMAGEID']
    accID = r['accID']
    logicalDB = r['logicalDB']

    if (qcMGIID == None):
        qcMGIID = ""
    if (qcIMAGEID == None):
        qcIMAGEID = ""

    if (discrepNum != oldDiscrepNum or
        qcMGIID != oldQCMGIID or qcIMAGEID != oldQCIMAGEID):
        if (oldDiscrepNum != 0):
            fp.write(discrepType[oldDiscrepNum - 1] + TAB + \
                     oldQCMGIID + TAB + oldQCIMAGEID + TAB + \
                     oldRefMGIID + TAB + oldRefIMAGEID + TAB + \
                     seqIDs + TAB + cloneIDs + TAB + mgiIDs + CRT)
        oldDiscrepNum = discrepNum
        oldQCMGIID = qcMGIID
        oldQCIMAGEID = qcIMAGEID
        oldRefMGIID = refMGIID
        oldRefIMAGEID = refIMAGEID
        seqIDs = ""
        cloneIDs = ""
        mgiIDs = ""

    if (logicalDB == "Sequence DB"):
        if (seqIDs == ""):
            seqIDs = accID
        else:
            seqIDs = seqIDs + "," + accID

    elif (logicalDB == "MGI"):
        if (mgiIDs == ""):
            mgiIDs = accID
        else:
            mgiIDs = mgiIDs + "," + accID

    else:
        if (cloneIDs == ""):
            cloneIDs = accID
        else:
            cloneIDs = cloneIDs + "," + accID

if (oldDiscrepNum != 0):
    fp.write(discrepType[oldDiscrepNum - 1] + TAB + \
             oldQCMGIID + TAB + oldQCIMAGEID + TAB + \
             oldRefMGIID + TAB + oldRefIMAGEID + TAB + \
             seqIDs + TAB + cloneIDs + TAB + mgiIDs + CRT)

reportlib.finish_nonps(fp)
