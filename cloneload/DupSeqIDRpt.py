#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of duplicate sequence IDs in the
#       MGI_CloneLoad_Accession table in the RADAR database.
#
#       The report output is formatted under the following headings:
#
#       1) Seq ID
#       2) RADAR Clone Name
#       3) Other Accession IDs For The Clone
#
#       This report assumes that the clone loader has been run and that
#       the data for the report has been populated in the
#       QC_CloneLoad_DupSeq table in the RADAR database.
#
# Usage:
#       DupSeqIDRpt.py  OutputDir  Server  RADAR  MGD  JobKey
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
mgdDB=sys.argv[4]
jobKey=sys.argv[5]

reportWidth = 102;
 

def getIDList(cloneKey, seqID):
    idList = []
    deleteList = []

    for d in results[0]:
        if d['_Clone_key'] == cloneKey and d['seqID'] == seqID:
            deleteList.append(d)
            if d['accID'] != seqID:
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


def writeSeq(seqID,cloneName,accList):
    while (len(accList) > 0):
        fp.write("%-8s %-40s " % (seqID,cloneName))
        seqID = ""
        cloneName = ""
        writeStrings(accList,4,12)
        fp.write(CRT)

    return


#
# Main
#
fp = reportlib.init(outputfile='DuplicateSeqID.rpt', outputdir=outputDir)

fp.write('SERVER=' + server + '  DATABASE=' + radarDB + ',' + mgdDB + 2*CRT)

fp.write(string.center('Duplicate Sequence ID Report',reportWidth) + 2*CRT)

fp.write('Seq ID   ' + \
         'RADAR Clone Name                         ' + \
         'Other Accession IDs For The Clone' + CRT)
fp.write('-------- ' + \
         '---------------------------------------- ' + \
         '----------------------------------------------------' + CRT)

db.set_sqlServer(server)
db.set_sqlDatabase(radarDB)

cmd = []
cmd.append('select seqID, cloneName, _Clone_key, accID ' + \
           'from QC_CloneLoad_DupSeq ' + \
           'where _JobStream_key = ' + jobKey + ' ' + \
           'order by seqID, cloneName, _Clone_key, accID')

results = db.sql(cmd, 'auto')

#for l in results:
#    for d in l:
#        print d
#    print

oldSeqID = ""
while len(results[0]) > 0:
    seqID = results[0][0]['seqID']
    cloneName = results[0][0]['cloneName']
    cloneKey = results[0][0]['_Clone_key']
    accList = getIDList(cloneKey,seqID)

#    print seqID
#    print cloneName
#    print cloneKey
#    print accList

    if seqID != oldSeqID:
        if oldSeqID != "":
            fp.write(CRT)
        writeSeq(seqID,cloneName,accList)
    else:
        writeSeq("",cloneName,accList)
    oldSeqID = seqID

reportlib.finish_nonps(fp)
