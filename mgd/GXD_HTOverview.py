#!/usr/local/bin/python

'''
#
# TR 12370
#
# Report:
#
# GXD HT Overview report
#    Col 1: List of AE ids loaded in to MGI typeKey=42, ldbKey=189
#    Col 2: GEO id, if applicable ldbKey=190
#    Col 3: experiment type vocabKey=121
#    Col 4: evaluation state  vocabKey=116
#    Col 5: study type vocabKey=124
#    Col 6: experimental variables, multiples separated by pipes vocabKey=122
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

fp = reportlib.init(sys.argv[0], 'GXD Overview QC', os.environ['QCOUTPUTDIR'])

results = db.sql('''select a1.accid as aeId, a2.accid as geoId, e._Experiment_key, 
	    t1.term as exptType, t2.term as evalState, t3.term as studyType, 
	    v._Term_key as varTermKey, vt.Term as varTerm
	from ACC_Accession a1, VOC_Term t1, VOC_Term t2, VOC_Term t3, 
	    GXD_HTExperiment e
	left outer join ACC_Accession a2 on (e._Experiment_key = a2._Object_key
	    and a2._MGIType_key = 42
	    and a2._LogicalDB_key = 190
	    and a2.preferred = 0)
	left outer join GXD_HTExperimentVariable v 
	    on (e._Experiment_key = v._Experiment_key )
	left outer join VOC_Term vt on (v._term_key = vt._term_key)
	where e._Experiment_key = a1._Object_key
	    and a1._MGIType_key = 42
	    and a1._LogicalDB_key = 189
	    and a1.preferred = 1
	    and e._ExperimentType_key = t1._Term_key
	    and e._EvaluationState_key = t2._Term_key
	    and e._StudyType_key = t3._Term_key''', 'auto')
exptDict = {}
for r in results:
    #    Col 1: List of AE ids loaded in to MGI typeKey=42, ldbKey=189
    #    Col 2: GEO id, if applicable ldbKey=190
    #    Col 3: experiment type vocabKey=121
    #    Col 4: evaluation state  vocabKey=116
    #    Col 5: study type vocabKey=124
    #    Col 6: experimental variables, multiples separated by '|' vocabKey=122
    exptKey = r['_Experiment_key']
    
    if not exptKey in exptDict:
	exptDict[exptKey] = []
    exptDict[exptKey].append(r)

ct = 0
fp.write('ArrayExpress ID%sGEO ID%sExperiment Type%sEvaluation State%sStudy Type%sVariables%s' % (TAB, TAB, TAB, TAB, TAB, CRT))
for key in exptDict:
    # if there are > 1 row then there are > 1 variable, all other info repeated
    r = exptDict[key][0]
    aeId = r['aeId']
    geoId = r['geoId']
    exptType = r['exptType']
    evalState = r['evalState']
    studyType = r['studyType']
    varList = []
    for r in exptDict[key]:
	varTerm = r['varTerm']
	# not all experiments have variable terms
	if varTerm != None:
	    varList.append(varTerm)
    varTerms = string.join(varList, '|')
    fp.write('%s%s%s%s%s%s%s%s%s%s%s%s' % (aeId, TAB, geoId, TAB, exptType, TAB,  evalState, TAB, studyType, TAB, varTerms, CRT ))
    ct += 1

fp.write('%sTotal:%s%s' % (CRT, ct, CRT))

