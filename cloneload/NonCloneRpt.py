#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of RADAR clones that have an MGI ID
#       that is associated with a non-clone object in MGD.
#
#       The report output is formatted under the following headings:
#
#       1) RADAR Clone Name
#       2) Sequence IDs For The RADAR Clone
#       3) Clone IDs For The RADAR Clone
#       4) MGI IDs (MGI Type)
#
#       This report assumes that the clone loader has been run and that
#       the data for the report has been populated in the
#       QC_CloneLoad_NonClone table in the RADAR database.
#
# Usage:
#       NonCloneRpt.py  OutputDir  Server  RADAR  MGD  JobKey
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

MGI_LIST = 0
CLONE_LIST = 1
SEQ_LIST = 2

#
# Main
#
outputDir=sys.argv[1]
server=sys.argv[2]
radarDB=sys.argv[3]
mgdDB=sys.argv[4]
jobKey=sys.argv[5]

reportWidth = 152;


def getMGIList(cloneKey):
    mgiList = []
    deleteList = []

    for d in results[MGI_LIST]:
        if d['_Clone_key'] == cloneKey:
            mgiList.append(d['mgiID']+'('+str(d['_MGIType_key'])+')')
            deleteList.append(d)

    for d in deleteList:
        results[MGI_LIST].remove(d)

    return mgiList


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


def writeClone(cloneName,mgiList,cloneList,seqList):
    while (len(mgiList) > 0 or len(cloneList) > 0 or len(seqList) > 0):
        fp.write("%-40s " % cloneName)
        if cloneName != "":
            cloneName = ""
        writeStrings(seqList,4,8)
        writeStrings(cloneList,3,12)
        writeStrings(mgiList,2,16)
        fp.write(CRT)

    return


#
# Main
#
fp = reportlib.init(outputfile='NonClone_mgiID.rpt', outputdir=outputDir,
                    sqlLogging = 0)

fp.write('SERVER=' + server + '  DATABASE=' + radarDB + ',' + mgdDB + 2*CRT)

fp.write(string.center('Non-Clone MGI ID Report',reportWidth) + 2*CRT)

fp.write('RADAR Clone Name                         ' + \
         'Sequence IDs For The RADAR Clone     ' + \
         'Clone IDs For The RADAR Clone           ' + \
         'MGI IDs (MGI Type)                ' + CRT)
fp.write('---------------------------------------- ' + \
         '------------------------------------ ' + \
         '--------------------------------------- ' + \
         '----------------------------------' + CRT)

db.set_sqlServer(server)
db.set_sqlDatabase(mgdDB)

cmd = []
cmd.append('select qc._Clone_key, c.cloneName, qc.mgiID, qc._MGIType_key ' + \
           'from ' + radarDB + '..QC_CloneLoad_NonClone qc, ' + \
                     radarDB + '..MGI_CloneLoad_Clone c ' + \
           'where qc._JobStream_key = ' + jobKey + ' and ' + \
                 'qc._Clone_key = c._Clone_key '
           'order by qc._Clone_key, c.cloneName, qc.mgiID, qc._MGIType_key')

cmd.append('select ca._Clone_key, ca.accID ' + \
           'from ' + radarDB + '..QC_CloneLoad_NonClone qc, ' + \
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

cmd.append('select ca._Clone_key, ca.accID ' + \
           'from ' + radarDB + '..QC_CloneLoad_NonClone qc, ' + \
                     radarDB + '..MGI_CloneLoad_Accession ca, ' + \
                    'ACC_LogicalDB db, ' + \
                    'MGI_SetMember sm, ' + \
                    'MGI_Set s ' + \
           'where qc._JobStream_key = ' + jobKey + ' and ' + \
                 'qc._Clone_key = ca._Clone_key and ' + \
                 'ca.logicalDB = db.name and ' + \
                 'db._LogicalDB_key = 9 ' + \
           'order by ca._Clone_key, ca.accID')

results = db.sql(cmd, 'auto')

#for l in results:
#    for d in l:
#        print d
#    print

while len(results[MGI_LIST]) > 0:
    cloneKey = results[MGI_LIST][0]['_Clone_key']
    cloneName = results[MGI_LIST][0]['cloneName']
    mgiList = getMGIList(cloneKey)
    cloneList = getIDList(CLONE_LIST,cloneKey)
    seqList = getIDList(SEQ_LIST,cloneKey)

#    print cloneKey
#    print cloneName
#    print mgiList
#    print cloneList
#    print seqList

    writeClone(cloneName,mgiList,cloneList,seqList)
    fp.write(CRT)

reportlib.finish_nonps(fp)
