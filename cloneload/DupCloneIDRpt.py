#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of duplicate clone IDs in the
#       MGI_CloneLoad_Accession table in the RADAR database.
#
#       The report output is formatted under the following headings:
#
#       1) Clone ID
#       2) RADAR Clone Name
#       3) Other Accession IDs For The Clone
#
#       This report assumes that the clone loader has been run and that
#       the data for the report has been populated in the
#       QC_CloneLoad_DupClone table in the RADAR database.
#
# Usage:
#       DupCloneIDRpt.py  OutputDir  Server  RADAR  MGD  JobKey
#
# Notes:
#
# History:
#
# dbm   10/27/2003
#       - created
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
mgdDB=sys.argv[4]
jobKey=sys.argv[5]

reportWidth = 106;


def getIDList(cloneKey, cloneID):
    idList = []
    deleteList = []

    for d in results[0]:
        if d['_Clone_key'] == cloneKey:
            deleteList.append(d)
            if d['accID'] != cloneID:
                idList.append(d['accID'])

    for d in deleteList:
        results[0].remove(d)

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


def writeClone(cloneID,cloneName,accList):
    while (len(accList) > 0):
        fp.write("%-12s %-40s " % (cloneID,cloneName))
        cloneID = ""
        cloneName = ""
        writeStrings(accList,4,12)
        fp.write(CRT)

    return


#
# Main
#
fp = reportlib.init(outputfile='DuplicateCloneID.rpt', outputdir=outputDir,
                    sqlLogging = 0)

fp.write('SERVER=' + server + '  DATABASE=' + radarDB + ',' + mgdDB + 2*CRT)

fp.write(string.center('Duplicate Clone ID Report',reportWidth) + 2*CRT)

fp.write('Clone ID     ' + \
         'RADAR Clone Name                         ' + \
         'Other Accession IDs For The Clone' + CRT)
fp.write('------------ ' + \
         '---------------------------------------- ' + \
         '----------------------------------------------------' + CRT)

db.set_sqlServer(server)
db.set_sqlDatabase(radarDB)

cmd = []
cmd.append('select cloneID, cloneName, _Clone_key, accID ' + \
           'from QC_CloneLoad_DupClone ' + \
           'where _JobStream_key = ' + jobKey + ' ' + \
           'order by cloneID, cloneName, _Clone_key, accID')

results = db.sql(cmd, 'auto')

#for l in results:
#    for d in l:
#        print d
#    print

oldCloneID = ""
while len(results[0]) > 0:
    cloneID = results[0][0]['cloneID']
    cloneName = results[0][0]['cloneName']
    cloneKey = results[0][0]['_Clone_key']
    accList = getIDList(cloneKey,cloneID)

#    print cloneID
#    print cloneName
#    print cloneKey
#    print accList

    if cloneID != oldCloneID:
        if oldCloneID != "":
            fp.write(CRT)
        writeClone(cloneID,cloneName,accList)
    else:
        writeClone("",cloneName,accList)
    oldCloneID = cloneID

reportlib.finish_nonps(fp)
