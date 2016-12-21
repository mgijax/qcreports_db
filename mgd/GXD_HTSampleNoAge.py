#!/usr/local/bin/python

'''
#
# TR 12370
#
# Report:
#
#  List of Samples whose Relevance = Yes and whose age is
#    Not Specified or Not Applicable
#
# Usage:
#       GXD_HTSampleNoAge.py
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
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'Samples whose Relevance = Yes but the age field is Not Applicable or Not Specified', os.environ['QCOUTPUTDIR'])

results = db.sql('''select a.accid as exptId, s.name, s.age
    from GXD_HTSample s, ACC_Accession a
    where _Relevance_key = 20475450
    and (age = 'Not Specified' or age = 'Not Applicable')
    and s._Experiment_key = a._Object_key
    and a._MGIType_key = 42
    and a._LogicalDB_key = 189
    and a.preferred = 1
    order by a.accid, s.name''', 'auto') 

fp.write('%sTotal:%s%s%s' % (CRT, len(results), CRT, CRT))
fp.write('AE ID%sSample Name%sAge%s' % (TAB, TAB, CRT))

for r in results:
    exptId = r['exptId']
    name = r['name']
    age = r['age']
    fp.write('%s%s%s%s%s%s' % (exptId, TAB, name, TAB, age, CRT))
