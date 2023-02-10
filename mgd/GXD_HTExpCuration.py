'''
#
# TR 12370
#
# Report:
#
# List of experiments whose 
#       (Curation State = Done)
#       AND (
#               Study Type=Not Curated 
#               OR Experimental Variables=Not Curated 
#               OR Experiment Type=Not Resolved
#               OR Evaluation != Yes
#       )
#
# Usage:
#       GXD_HTExpCuration.py
#
# Notes:
#
# History:
#
# lec   02/09/2023
#       - wts2-1097/fl2-203/add Experiments where Curation State=Done and Evaluation !=Yes
#
# sc   11/04/2016
#       - TR12370 created
#
'''

import sys
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], '\nExperiments where Curation State=Done and (Study Type=Not Curated OR Experimental Variables=Not Curated OR Experiment Type=Not Resolved OR Evaluation!= Yes)', os.environ['QCOUTPUTDIR'])

results = db.sql('''
        -- curation state = Done
        select distinct a.accid, hte._Experiment_key
        from ACC_Accession a, GXD_HTExperiment hte, GXD_HTExperimentVariable hv
        where hte._CurationState_key = 20475421
        and hte._Experiment_key = hv._Experiment_key
        and hte._Experiment_key = a._Object_key
        and a._MGIType_key = 42
        and a._LogicalDB_key in (189, 190)
        and a.preferred = 1
        and (
                -- study type =  Not Curated
                hte._StudyType_key = 20475461
                -- experiment type = Not Resolved
                or hte._ExperimentType_key = 20475438
                -- evaluation state != yes
                or hte._evaluationstate_key != 20225942
                --  experimental variables = Not Curated
                or hv._Term_key = 20475439
        )
        order by a.accid
        ''', 'auto')

for r in results:
    exptKey = r['_Experiment_key']
    accid = r['accid']
    fp.write('%s%s' % (accid, CRT))

fp.write('%sTotal:%s%s' % (CRT, len(results), CRT))
