#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of RADAR clones that map to multiple
#       MGI clone objects in MGD via a set of accession IDs.
#
#       The report output is formatted under the following headings:
#
#       1) RADAR Clone Name
#       2) MGI ID
#       3) MGI Clone Name
#       4) Accession IDs For The RADAR Clone
#
#       This report assumes that the clone loader has been run and that
#       the data for the report has been populated in the
#       QC_CloneLoad_MultiClone table in the RADAR database.
#
# Usage:
#       MultiCloneRpt.py  OutputDir  Server  RADAR  MGD  JobKey
#
# Notes:
#
# History:
#
# dbm   8/6/2003
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

MGI_LIST = 0
ACC_LIST = 1


def getIDList(listNumber, cloneKey, mgiID):
    idList = []
    deleteList = []

    for d in results[listNumber]:
        if (d['_Clone_key'] == cloneKey and d['mgiID'] == mgiID):
            idList.append(d['accID'])
            deleteList.append(d)

    for d in deleteList:
        results[listNumber].remove(d)

    return idList


def writeStrings(list,maxStr,lenStr):
    count = 0
    printStr = ""
    deleteList = []

    for i in range(len(list)):
        if count == maxStr:
            break;
        printStr = printStr + list[i]
        if i < (len(list) - 1):
            printStr = printStr + ","
        deleteList.append(list[i])
        count = count + 1

    format = "%-"+str(maxStr * (lenStr + 1))+"s "
    fp.write(format % printStr)

    for d in deleteList:
        list.remove(d)

    return


def writeClone(rCloneName,mgiID,mCloneName,accList):
    while len(accList) > 0:
        fp.write("%-40s %-12s %-40s " % (rCloneName,mgiID,mCloneName))
        if rCloneName != "":
            rCloneName = ""
            mgiID = ""
            mCloneName = ""
        writeStrings(accList,4,8)
        fp.write(CRT)

    return


#
# Main
#
outputDir=sys.argv[1]
server=sys.argv[2]
radarDB=sys.argv[3]
mgdDB=sys.argv[4]
jobKey=sys.argv[5]

reportWidth = 147;

fp = reportlib.init(outputfile='Many_MGI_Clones.rpt', outputdir=outputDir,
                    sqlLogging = 0)

fp.write('SERVER=' + server + '  DATABASE=' + radarDB + ',' + mgdDB + 2*CRT)

fp.write(string.center('Multiple MGI Clone Report',reportWidth) + 2*CRT)

fp.write('RADAR Clone Name                         ' + \
         'MGI ID       ' + \
         'MGI Clone Name                           ' + \
         'Accession IDs For The RADAR Clone                   ' + CRT)
fp.write('---------------------------------------- ' + \
         '------------ ' + \
         '---------------------------------------- ' + \
         '----------------------------------------------------' + CRT)

db.set_sqlServer(server)
db.set_sqlDatabase(mgdDB)

cmd = []
cmd.append('select distinct qc._Clone_key, c.cloneName, qc.mgiID, p.name ' + \
           'from ' + radarDB + '..QC_CloneLoad_MultiClone qc, ' + \
                     radarDB + '..MGI_CloneLoad_Clone c, ' + \
                    'ACC_Accession a, ' + \
                    'PRB_Probe p ' + \
           'where qc._JobStream_key = ' + jobKey + ' and ' + \
                 'qc._Clone_key = c._Clone_key and ' + \
                 'qc.mgiID = a.accID and ' + \
                 'a._LogicalDB_key = 1 and ' + \
                 'a._MGIType_key = 3 and ' + \
                 'a.Preferred = 1 and ' + \
                 'a._Object_key = p._Probe_key ' + \
           'order by qc._Clone_key, c.cloneName, qc.mgiID')

cmd.append('select qc._Clone_key, qc.mgiID, qc.accID ' + \
           'from ' + radarDB + '..QC_CloneLoad_MultiClone qc ' + \
           'where qc._JobStream_key = ' + jobKey + ' ' + \
           'order by qc._Clone_key, qc.mgiID, qc.accID')

results = db.sql(cmd, 'auto')

#for l in results:
#    for d in l:
#        print d
#    print

rCloneNameOld = ""
for r in results[MGI_LIST]:
    cloneKey = r['_Clone_key']
    rCloneName = r['cloneName']
    mgiID = r['mgiID']
    mCloneName = r['name']
    accList = getIDList(ACC_LIST,cloneKey,mgiID)

#    print cloneKey
#    print rCloneName
#    print mgiID
#    print mCloneName
#    print accList

    if rCloneName != rCloneNameOld:
        if rCloneNameOld != "":
            fp.write(CRT)
        writeClone(rCloneName,mgiID,mCloneName,accList)
    else:
        writeClone("",mgiID,mCloneName,accList)
    rCloneNameOld = rCloneName

reportlib.finish_nonps(fp)
