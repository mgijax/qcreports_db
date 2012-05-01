#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of input records that have duplicate
#       Sequence IDs.
#
#       The report contains the following tab-delimited fields:
#
#       1) Sequence ID
#       2) IMAGE ID (if it is not null)
#       3) MGC ID (if it is not null)
#
#       This report assumes that the MGC load has been run and the data for
#       the report has been populated in the QC_MGCLoad_Sequence_Duplicate
#       table in the RADAR database.
#
# Usage:
#       DuplicateSequenceRpt.py  OutputDir  Server  RADAR  JobKey
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
outputDir=sys.argv[1]
server=sys.argv[2]
radarDB=sys.argv[3]
jobKey=sys.argv[4]
 
fp = reportlib.init(outputfile='DuplicateSequence.rpt', outputdir=outputDir,
                    printHeading = None, sqlLogging = 0)

db.set_sqlServer(server)
db.set_sqlDatabase(radarDB)

cmd = []
cmd.append('select d.seqID, d.imageID, d.mgcID ' + \
           'from DP_MGC_Clones d ' + \
           'where exists (select 1 ' + \
                         'from QC_MGCLoad_Sequence_Duplicate q ' + \
                         'where q._MGCClone_key = d._MGCClone_key and ' + \
                               'q._JobStream_key = ' + jobKey + ') ' + \
           'order by d.seqID, d.imageID, d.mgcID')

results = db.sql(cmd, 'auto')

for r in results[0]:
    seqID = r['seqID']
    imageID = r['imageID']
    mgcID = r['mgcID']
    if (seqID == None):
        seqID = ""
    if (imageID == None):
        imageID = ""
    if (mgcID == None):
        mgcID = ""
    fp.write(seqID + TAB + imageID + TAB + mgcID + CRT)

reportlib.finish_nonps(fp)
