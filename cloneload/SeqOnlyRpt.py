#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of RADAR clones that only map to an
#       MGI clone object in MGD via sequence IDs.
#
#       The report output is formatted under the following headings:
#
#       1) RADAR Clone Name
#       2) Sequence IDs For The RADAR Clone
#       3) Clone IDs For The RADAR Clone
#       4) MGI ID
#       5) MGI Clone Name
#
#       This report assumes that the clone loader has been run and that
#       the data for the report has been populated in the
#       QC_CloneLoad_SeqOnly table in the RADAR database.
#
# Usage:
#       SeqOnlyRpt.py  OutputDir  Server  RADAR  MGD  JobKey
#
# Notes:
#
# History:
#
# dbm   8/6/2003
#       - created
#
# dbm   11/4/2004
#       - use new "Clone Collection" set
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
CLONE_LIST = 1
SEQ_LIST = 2


def getIDList(listNumber, cloneKey):
    idList = []
    deleteList = []

    for d in results[listNumber]:
        if d['_Clone_key'] == cloneKey:
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


def writeClone(rCloneName,mgiID,mCloneName,cloneList,seqList):
    while (len(cloneList) > 0 or len(seqList) > 0):
        fp.write("%-40s " % rCloneName)
        if rCloneName != "":
            rCloneName = ""
        writeStrings(seqList,4,8)
        writeStrings(cloneList,3,12)
        fp.write("%-12s %-40s" % (mgiID,mCloneName))
        if mCloneName != "":
            mgiID = ""
            mCloneName = ""
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

reportWidth = 171;

fp = reportlib.init(outputfile='GBSeq_Only.rpt', outputdir=outputDir)

fp.write('SERVER=' + server + '  DATABASE=' + radarDB + ',' + mgdDB + 2*CRT)

fp.write(string.center('Sequence ID Only Report',reportWidth) + 2*CRT)

fp.write('RADAR Clone Name                         ' + \
         'Sequence IDs For The RADAR Clone     ' + \
         'Clone IDs For The RADAR Clone           ' + \
         'MGI ID       ' + \
         'MGI Clone Name                          ' + CRT)
fp.write('---------------------------------------- ' + \
         '------------------------------------ ' + \
         '--------------------------------------- ' + \
         '------------ ' + \
         '----------------------------------------' + CRT)

db.set_sqlServer(server)
db.set_sqlDatabase(mgdDB)

cmd = []
cmd.append('select distinct qc._Clone_key, c.cloneName, qc.mgiID, p.name ' + \
           'from ' + radarDB + '..QC_CloneLoad_SeqOnly qc, ' + \
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

cmd.append('select distinct ca._Clone_key, ca.accID ' + \
           'from ' + radarDB + '..QC_CloneLoad_SeqOnly qc, ' + \
                     radarDB + '..MGI_CloneLoad_Accession ca, ' + \
                    'ACC_LogicalDB db, ' + \
                    'MGI_SetMember sm, ' + \
                    'MGI_Set s ' + \
           'where qc._JobStream_key = ' + jobKey + ' and ' + \
                 'qc._Clone_key = ca._Clone_key and ' + \
                 'ca.logicalDB = db.name and ' + \
                 'db._LogicalDB_key = sm._Object_key and ' + \
                 'sm._Set_key = s._Set_key and ' + \
                 's.name = "Clone Collection (all)" ' + \
           'order by ca._Clone_key, ca.accID')

cmd.append('select qc._Clone_key, qc.seqID "accID" ' + \
           'from ' + radarDB + '..QC_CloneLoad_SeqOnly qc ' + \
           'where qc._JobStream_key = ' + jobKey + ' ' + \
           'order by qc._Clone_key, qc.seqID')

results = db.sql(cmd, 'auto')

#for l in results:
#    for d in l:
#        print d
#    print

for r in results[MGI_LIST]:
    cloneKey = r['_Clone_key']
    rCloneName = r['cloneName']
    mgiID = r['mgiID']
    mCloneName = r['name']
    cloneList = getIDList(CLONE_LIST,cloneKey)
    seqList = getIDList(SEQ_LIST,cloneKey)

#    print cloneKey
#    print rCloneName
#    print mgiID
#    print mCloneName
#    print cloneList
#    print seqList

    writeClone(rCloneName,mgiID,mCloneName,cloneList,seqList)
    fp.write(CRT)

reportlib.finish_nonps(fp)
