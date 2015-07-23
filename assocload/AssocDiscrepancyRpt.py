#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of discrepancies where an
#       accession ID/logical DB is associated with too many MGI objects
#       or the wrong type of MGI object(s).
#
#       The report output is formatted under the following headings:
#
#       1) Target Acc ID
#       2) Target Logical DB
#       3) Target MGI Object - The MGI ID for the target MGI object.
#       4) Target MGI Type - The MGI type of the target MGI object.
#       5) Acc ID - The accession ID to be associated with the target
#                   MGI object.
#       6) Logical DB - The logical DB for the accession ID that is to be
#                       associated with the target MGI object.
#       7) MGI Object - The MGI ID for the associated MGI object.
#       8) MGI Type - The MGI type of the associated MGI object.
#       9) Message - A message indicating the type/count of MGI objects
#                    that the accession ID/logical DB are associated with.
#
#       This report assumes that the association loader has been run and
#       the data for the report has been populated in the
#       QC_AssocLoad_Assoc_Discrep table in the RADAR database.
#
# Usage:
#       AssocDiscrepancyRpt.py  OutputDir  Server  RADAR  MGD  JobKey
#
# Notes:
#
# History:
#
# dbm   01/24/2005
#       - created
#
'''
 
import sys 
import os
import string
import reportlib
import db

#db.setTrace()
db.setAutoTranslate()
db.setAutoTranslateBE()

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
 
fp = reportlib.init(outputfile='AssocDiscrepancy.rpt', outputdir=outputDir,
                    sqlLogging = 0)

fp.write('SERVER=' + server + '  DATABASE=' + radarDB + ',' + mgdDB + 2*CRT)

fp.write(string.center('Associate Discrepancy Report',reportWidth) + 2*CRT)

fp.write('Target Acc ID        Target Logical DB    ' + \
         'Target MGI Object    Target MGI Type      ' + \
         'Acc ID               Logical DB           ' + \
         'MGI Object           MGI Type             ' + \
         'Message' + CRT)
fp.write('-------------------- -------------------- ' + \
         '-------------------- -------------------- ' + \
         '-------------------- -------------------- ' + \
         '-------------------- -------------------- ' + \
         '------------------------------------------------------------' + CRT)

db.set_sqlServer(server)
db.set_sqlDatabase(mgdDB)

cmd = []
cmd.append('select q._QCRecord_key, ' + \
                  'q.tgtAccID as tgtAccID, db1.name as tgtLogicalDB, ' + \
                  'm1.name as tgtMGIType, ' + \
                  'q.accID as accID, db2.name as logicalDB, ' + \
                  'm2.name as mgiType, ' + \
                  'q.message ' + \
           'from ' + radarDB + '..QC_AssocLoad_Assoc_Discrep q, ' + \
                'ACC_LogicalDB db1, ' + \
                'ACC_LogicalDB db2, ' + \
                'ACC_MGIType m1, ' + \
                'ACC_MGIType m2 ' + \
           'where q._TgtLogicalDB_key = db1._LogicalDB_key and ' + \
                 'q._TgtMGIType_key = m1._MGIType_key and ' + \
                 'q._LogicalDB_key = db2._LogicalDB_key and ' + \
                 'q._MGIType_key = m2._MGIType_key and ' + \
                 'q._JobStream_key = ' + jobKey + ' ' + \
           'order by q.tgtAccID, db1.name')

cmd.append('select q._QCRecord_key, a.accID as mgiID ' + \
           'from ' + radarDB + '..QC_AssocLoad_Assoc_Discrep q, ' + \
                'ACC_Accession a ' + \
           'where q._TgtMGIType_key = a._MGIType_key and ' + \
                 'q._TgtObject_key = a._Object_key and ' + \
                 'a._LogicalDB_key = 1 and ' + \
                 'a.preferred = 1 and ' + \
                 'q._JobStream_key = ' + jobKey)

cmd.append('select q._QCRecord_key, a.accID as mgiID ' + \
           'from ' + radarDB + '..QC_AssocLoad_Assoc_Discrep q, ' + \
                'ACC_Accession a ' + \
           'where q._MGIType_key = a._MGIType_key and ' + \
                 'q._Object_key = a._Object_key and ' + \
                 'a._LogicalDB_key = 1 and ' + \
                 'a.preferred = 1 and ' + \
                 'q._JobStream_key = ' + jobKey)

results = db.sql(cmd, 'auto')

tgtObjs = {}
for r in results[1]:
    tgtObjs[r['_QCRecord_key']] = r['mgiID']

assocObjs = {}
for r in results[2]:
    assocObjs[r['_QCRecord_key']] = r['mgiID']

for r in results[0]:
    key = r['_QCRecord_key']
    tgtAccID = r['tgtAccID']
    tgtLogicalDB = r['tgtLogicalDB']
    tgtMGIType = r['tgtMGIType']
    accID = r['accID']
    logicalDB = r['logicalDB']
    mgiType = r['mgiType']
    message = r['message']

#    tgtMGIID = tgtObjs.get(key,' ')
#    mgiID = assocObjs.get(key,' ')

    if tgtObjs.has_key(key):
        tgtMGIID = tgtObjs[key]
    else:
        tgtMGIID = ' '
    if assocObjs.has_key(key):
        mgiID = assocObjs[key]
    else:
        mgiID = ' '

    fp.write("%-20s %-20s %-20s %-20s %-20s %-20s %-20s %-20s %-60s" %
            (tgtAccID, tgtLogicalDB, tgtMGIID, tgtMGIType,
             accID, logicalDB, mgiID, mgiType, message))
    fp.write(CRT)

fp.write(CRT + 'Number of Discrepancies: ' + str(len(results[0])) + CRT)

reportlib.finish_nonps(fp)
