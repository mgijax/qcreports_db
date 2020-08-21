#
# Report:
#       This script produces a report of discrepancies where a target
#       accession ID/logical DB is not associated with only one object
#       in MGI.
#
#       The report output is formatted under the following headings:
#
#       1) Acc ID
#       2) Logical DB
#       3) MGI Object - The MGI ID for the associated MGI object.
#       4) MGI Type - The MGI type of the associated MGI object.
#       5) Expected Type - The expected MGI type for the target MGI object
#                          for this job stream.
#       6) Message - A message indicating the type/count of MGI objects
#                    that the accession ID/logical DB are associated with.
#
#       This report assumes that the association loader has been run and
#       the data for the report has been populated in the
#       QC_AssocLoad_Target_Discrep table in the RADAR database.
#
# Usage:
#       TargetDiscrepancyRpt.py  OutputDir  Server  RADAR  MGD  JobKey
#
# Notes:
#
# History:
#
# dbm   01/24/2005
#       - created
#
 
import sys 
import os
import reportlib
import db

#db.setTrace()

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
mgdDB=sys.argv[4]
jobKey=sys.argv[5]

reportWidth = 165;
 
fp = reportlib.init(outputfile='TargetDiscrepancy.rpt', outputdir=outputDir,
                    sqlLogging = 0)

fp.write('SERVER=' + server + '  DATABASE=' + radarDB + ',' + mgdDB + 2*CRT)

fp.write(str.center('Target Discrepancy Report',reportWidth) + 2*CRT)

fp.write('Acc ID               Logical DB           ' + \
         'MGI Object           MGI Type             Expected Type        ' + \
         'Message' + CRT)
fp.write('-------------------- -------------------- ' + \
         '-------------------- -------------------- -------------------- ' + \
         '------------------------------------------------------------' + CRT)

db.set_sqlServer(server)
db.set_sqlDatabase(mgdDB)

cmd = []
cmd.append('select q._QCRecord_key, q.accID, db.name as logicalDB, ' + \
                  'a.accID as mgiID, m.name as mgiType, ' + \
                  'q.expectedType, q.message ' + \
           'from ' + radarDB + '.QC_AssocLoad_Target_Discrep q, ' + \
                'ACC_Accession a, ' + \
                'ACC_LogicalDB db, ' + \
                'ACC_MGIType m ' + \
           'where q._LogicalDB_key = db._LogicalDB_key and ' + \
                 'q._MGIType_key = a._MGIType_key and ' + \
                 'q._Object_key = a._Object_key and ' + \
                 'a._LogicalDB_key = 1 and ' + \
                 'a.preferred = 1 and ' + \
                 'q._MGIType_key = m._MGIType_key and ' + \
                 'q._JobStream_key = ' + jobKey + ' ' + \
           'union ' + \
           'select q._QCRecord_key, q.accID, db.name as logicalDB, ' + \
                  'null as mgiID, null as mgiType, ' + \
                  'q.expectedType, q.message ' + \
           'from ' + radarDB + '.QC_AssocLoad_Target_Discrep q, ' + \
                'ACC_LogicalDB db ' + \
           'where q._LogicalDB_key = db._LogicalDB_key and ' + \
                 'q._MGIType_key is null and ' + \
                 'q._JobStream_key = ' + jobKey + ' ' + \
           'order by accID, logicalDB')

results = db.sql(cmd, 'auto')

for r in results[0]:
    accID = r['accID']
    logicalDB = r['logicalDB']
    mgiID = r['mgiID']
    mgiType = r['mgiType']
    expType = r['expectedType']
    message = r['message']

    if (mgiID == None):
        mgiID = ""
    if (mgiType == None):
        mgiType = ""

    fp.write("%-20s %-20s %-20s %-20s %-20s %-60s" %
            (accID, logicalDB, mgiID, mgiType, expType, message))
    fp.write(CRT)

fp.write(CRT + 'Number of Discrepancies: ' + str(len(results[0])) + CRT)

reportlib.finish_nonps(fp)
