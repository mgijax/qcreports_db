
'''
#
# TR 12370
#
# Report:
#
# List of Samples whose Relevance = Yes but the structure field is null--
# report should list experiment id and sample name 
#
# Usage:
#       GXD_HTSampleNoStructure.py
#
# Notes:
#
# History:
#
# sc   11/09/2061
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

fp = reportlib.init(sys.argv[0], 'Samples whose Relevance = Yes but the structure field is null', os.environ['QCOUTPUTDIR'])

results = db.sql('''select a.accid as exptId, s.name
    from GXD_HTSample s, ACC_Accession a
    where _Relevance_key = 20475450
    and _Emapa_key is null
    and s._Experiment_key = a._Object_key
    and a._MGIType_key = 42
    and a._LogicalDB_key in (189, 190)
    and a.preferred = 1 
    order by a.accid, s.name''', 'auto') 

fp.write('%sTotal:%s%s%s' % (CRT, len(results), CRT, CRT))
fp.write('AE ID%sSample Name%s' % (TAB, CRT))

for r in results:
    exptId = r['exptId']
    name = r['name']
    fp.write('%s%s%s%s' % (exptId, TAB, name, CRT))
