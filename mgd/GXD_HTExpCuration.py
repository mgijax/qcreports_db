
'''
#
# TR 12370
#
# Report:
#
# List of experiments whose Curation State = Done but Study Type or Experimental
#	 Variables = Not Curated or Experiment Type = Not Resolved
#
# Usage:
#       GXD_HTExpCuration.py
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

notCuratedStudyTypeList = []
notCuratedVarList = []
expTypeNRList = []
doneCurState = 20475421

fp = reportlib.init(sys.argv[0], 'Experiments where Curation State=Done and (Study Type=Not Curated OR Experimental Variables=Not Curated OR Experiment Type=Not Resolved)', os.environ['QCOUTPUTDIR'])

results = db.sql('''select _Experiment_key
        from GXD_HTExperiment
        where _StudyType_key = 20475461''', 'auto') # Not Curated
for r in results:
    notCuratedStudyTypeList.append(r['_Experiment_key'])

results = db.sql('''select _Experiment_key from GXD_HTExperimentVariable
        where _Term_key = 20475439''', 'auto') # Not Curated
for r in results:
        notCuratedVarList.append(r['_Experiment_key'])


results = db.sql('''select _Experiment_key 
        from GXD_HTExperiment
        where _ExperimentType_key = 20475438''', 'auto') # Not Resolved
for r in results:
    expTypeNRList.append(r['_Experiment_key'])


results = db.sql('''select a.accid, hte._Experiment_key
        from ACC_Accession a, GXD_HTExperiment hte
        where hte._CurationState_key = 20475421
        and hte._Experiment_key = a._Object_key
        and a._MGIType_key = 42
        and a._LogicalDB_key in (189, 190)
        and a.preferred = 1''', 'auto') # Done

ct = 0
for r in results:
    exptKey = r['_Experiment_key']
    accid = r['accid']
    if exptKey in notCuratedStudyTypeList or exptKey in notCuratedVarList or exptKey in expTypeNRList:
        ct += 1
        fp.write('%s%s' % (accid, CRT))

fp.write('%sTotal:%s%s' % (CRT, ct, CRT))
