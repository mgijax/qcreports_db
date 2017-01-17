#!/usr/local/bin/python

'''
#
# TR 12370
#
# Report:
#
# List of PubMed ids associated with experiments whose curation state = done that are not in the MasterBib; this is for Nancy/Janice 
#
# Usage:
#       GXD_HTNoMasterBib.py
#
# Notes:
#
# History:
#
# sc   11/04/2061
#       - TR12370 created
#
'''

import sys
import os
import string
import reportlib
import db

db.setTrace()
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'List of PubMed ids associated with experiments whose curation state = done that are not in the MasterBib', os.environ['QCOUTPUTDIR'])

fp.write('%sPlease get papers, select for "GXD HT Exp" in MasterBib and add to secondary triage folder.%s%s' % (CRT, CRT, CRT))

fp.write('AE ID%sPubMed ID(s)%s' % (TAB, CRT))

results = db.sql('''select a.accid as pubMedId, a._Object_key as _Refs_key
        from ACC_Accession a
        where a._LogicalDB_key = 29
        and a._MGIType_key = 1 
        and a.preferred = 1''', 'auto')

dbPubMedList = []
for r in results:
    dbPubMedList.append(r['pubMedId'])

results = db.sql('''select e._Experiment_key, a.accid as exptId, p.value as pubMedId
        from GXD_HTExperiment e, ACC_Accession a, MGI_Property p
        where e._CurationState_key = 20475421
        and e._Experiment_key = a._Object_key
        and a._MGIType_key = 42
        and a._LogicalDB_key = 189
        and a.preferred = 1
        and e._Experiment_key = p._Object_key
        and p._PropertyTerm_key = 20475430
        and p._PropertyType_key = 1002
	order by a.accid''', 'auto')

exptDict = {}
for r in results:
    exptKey = r['_Experiment_key']
    exptId = r['exptId']
    pubMedId = r['pubMedId']
    if exptId not in exptDict:
	exptDict[exptId] = []
    exptDict[exptId].append(pubMedId)

ct = 0
for exptId in sorted(exptDict):
    notInList = []
    for pubMedId in exptDict[exptId]:
	if pubMedId not in dbPubMedList:
	    notInList.append(pubMedId)
    if notInList:
 	ct += 1
	fp.write('%s%s%s%s' % (exptId, TAB, string.join(notInList, ', '), CRT))

fp.write('%sTotal:%s%s' % (CRT, ct, CRT))


