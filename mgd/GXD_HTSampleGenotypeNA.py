
'''
#
# TR 12370
#
# Report:
#
#   List of Samples whose Relevance = Yes but whose genotype is Not Applicable 
#      (MGI:2166309 key =  -2)
#
# Usage:
#       GXD_HTSampleGenotypeNA.py
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
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

fp = reportlib.init(sys.argv[0], 'Samples whose Relevance = Yes but whose genotype is Not Applicable (MGI:2166309)', os.environ['QCOUTPUTDIR'])

results = db.sql('''select a.accid as exptId, s.name
    from GXD_HTSample s, ACC_Accession a
    where _Relevance_key = 20475450
    and _Genotype_key = -2
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

reportlib.finish_nonps(fp)
