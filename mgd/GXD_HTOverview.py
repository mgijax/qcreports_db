
'''
#
# TR 12370
#
# Report:
#
# GXD HT Overview report
#    Col 1: List of primary ids loaded in to MGI typeKey=42, ldbKey in (189, 190)
#    Col 2: secondary GEO id, if applicable ldbKey=190
#    Col 3: experiment type vocabKey=121
#    Col 4: evaluation state  vocabKey=116
#    Col 5: study type vocabKey=124
#    Col 6: curation state vocabKey=117
#    Col 7: experimental variables, multiples separated by pipes vocabKey=122
#    Col 8: In Expression Atlas Set Y/N
#    Col 9: In RNA-Seq Load Set Y/N
#
#    monthly run sufficient for this one
#    make in a format that will load into excel easily (such as tab delimited)
#
# Usage:
#       GXD_HTOverview.py
#
# Notes:
#
# History:
#
# sc    07/30/2021
#       - YAKS project - load GEO experiments epic
#       - update to take primary id of both AE and GEO
#
# sc	08/23/2019
#	- GRSD project story 290, add columns for in RNA-Seq Load and 
#	    Expression Atlas sets
#
# sc	04/06/2017
#	- TR12523 add curation state as field 5
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

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

# experments in this list are in the Expression Atlas set
eaList = []

# experiments in this list are in the RNA-Seq Load set
rnaSeqList = []

results = db.sql('''select sm._object_key 
        from MGI_SetMember sm, MGI_Set s
        where s.name = 'Expression Atlas Experiments'
        and s._Set_key = sm._Set_key''', 'auto')
for r in results:
    eaList.append(r['_object_key'])

results = db.sql('''select sm._object_key
        from MGI_SetMember sm, MGI_Set s
        where s.name = 'RNASeq Load Experiments'
        and s._Set_key = sm._Set_key''', 'auto')
for r in results:
    rnaSeqList.append(r['_object_key'])

fp = reportlib.init(sys.argv[0], 'GXD Overview QC', os.environ['QCOUTPUTDIR'])

results = db.sql('''select a1.accid as aeId, a2.accid as geoId, e._Experiment_key, 
            t1.term as exptType, t2.term as evalState, t3.term as studyType, 
            t4.term as curationState, v._Term_key as varTermKey, 
            vt.Term as varTerm
        from ACC_Accession a1, VOC_Term t1, VOC_Term t2, VOC_Term t3, 
            VOC_Term t4, GXD_HTExperiment e
        left outer join ACC_Accession a2 on (e._Experiment_key = a2._Object_key
            and a2._MGIType_key = 42
            and a2._LogicalDB_key = 190
            and a2.preferred = 0)
        left outer join GXD_HTExperimentVariable v 
            on (e._Experiment_key = v._Experiment_key )
        left outer join VOC_Term vt on (v._term_key = vt._term_key)
        where e._Experiment_key = a1._Object_key
            and a1._MGIType_key = 42
            and a1._LogicalDB_key in (189, 190)
            and a1.preferred = 1
            and e._ExperimentType_key = t1._Term_key
            and e._EvaluationState_key = t2._Term_key
            and e._StudyType_key = t3._Term_key
            and e._CurationState_key = t4._Term_key''', 'auto')
exptDict = {}
for r in results:
    #    Col 1: List of AE ids loaded in to MGI typeKey=42, ldbKey=189
    #    Col 2: GEO id, if applicable ldbKey=190
    #    Col 3: experiment type vocabKey=121
    #    Col 4: evaluation state  vocabKey=11
    #    Col 5: study type vocabKey=124
    #    Col 6: curationState vocabKey=117
    #    Col 7: experimental variables, multiples separated by '|' vocabKey=122
    #    Col 8: In Expression Atlas Set Y/N
    #    Col 9: In RNA-Seq Load Set Y/N

    exptKey = r['_Experiment_key']
    
    if not exptKey in exptDict:
        exptDict[exptKey] = []
    exptDict[exptKey].append(r)

ct = 0
fp.write('Primary ID%sSecondary ID%sExperiment Type%sEvaluation State%sStudy Type%sCuration State%sVariables%sExpression Atlas?%sRNA-Seq Load?%s' % (TAB, TAB, TAB, TAB, TAB, TAB, TAB, TAB, CRT))
for key in exptDict:
    # if there are > 1 row then there are > 1 variable, all other info repeated
    r = exptDict[key][0]
    aeId = r['aeId']
    geoId = r['geoId']
    exptType = r['exptType']
    evalState = r['evalState']
    studyType = r['studyType']
    curationState = r['curationState']
    varList = []
    for r in exptDict[key]:
        varTerm = r['varTerm']
        # not all experiments have variable terms
        if varTerm != None:
            varList.append(varTerm)
    varTerms = '|'.join(varList)
    eaSet = 'No'
    if key in eaList:
        eaSet = 'Yes'
    rnaSeqSet = 'No'
    if key in rnaSeqList:
        rnaSeqSet = 'Yes'
    fp.write('%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (aeId, TAB, geoId, TAB, exptType, TAB,  evalState, TAB, studyType, TAB, curationState, TAB, varTerms, TAB, eaSet, TAB, rnaSeqSet, CRT ))
    ct += 1

fp.write('%sTotal:%s%s' % (CRT, ct, CRT))
