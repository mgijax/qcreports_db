
'''
#
# TR 12370
#
# Report:
#
#   Samples whose Relevance =Yes but whose Theiler stages and age fields are incompatible; 
#	need one report for embryonic, another for postnatal
#
# Usage:
#       GXD_HTSampleIncompAgeAndTS.py
# 
# Notes:
#
# History:
#
# sc   11/10/2061
#       - TR12370 created
#
'''

import sys
import os
import string
import reportlib
import db
import re

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'Samples whose Relevance = Yes but whose Theiler stages and age fields are incompatible', os.environ['QCOUTPUTDIR'])

fp.write('%sEmbryonic Age, excludes TS 27, 28%s' % (CRT, CRT))
# Get "embryonic day" age; exclude TS 27,28
db.sql(''' select s._Experiment_key, s.name, s.age, t.stage, t.dpcMin, t.dpcMax
    into temporary table temp1
    from GXD_HTSample s, GXD_Theilerstage t
    where s._Stage_key = t._Stage_key
    and s.age like 'embryonic day%' and
    t.stage not in (27, 28)''', None)
db.sql('''create index idx1 on temp1(_Experiment_key)''', None)
results = db.sql('''select distinct a.accID as exptId, t.*
    from temp1 t, ACC_Accession a
    where t._Experiment_key = a._Object_key
    and a._MGIType_key = 42
    and a._LogicalDB_key in (189, 190)
    and a.preferred = 1
    order by a.accID, t.name''', 'auto') 

s = ''
ct = 0

for r in results:
    age = r['age']
    m = re.search('[0-9]',age)
    if m == None:
        s = s + r['exptId'] + TAB + r['name'] + TAB + r['age'] + TAB + str(r['stage'])  + CRT
        ct += 1
        continue

    start = m.start()
    range = age[start:]

    # parse by range "-" or list ","

    m = re.search('[-,]', range)

    if m == None:
        minAge = float(range)
        maxAge = minAge
    else:
        delim = m.start()
        minAge = float(range[0:delim])
        maxAge = float(range[delim+1:])

    dpcMin = r['dpcMin']
    dpcMax = r['dpcMax']

    # If the age min is below the dpc min or age max is above the dpc max, print

    if (minAge < dpcMin or maxAge > dpcMax):
        s = s + r['exptId'] + TAB + r['name'] + TAB + r['age'] + TAB + str(r['stage']) +  CRT
        ct += 1

fp.write('%sTotal: %s%s' % (CRT, ct, CRT))
fp.write('Experiment ID%sName%sAge%sStage%s' % (TAB, TAB, TAB, CRT))
fp.write(s)


fp.write('%sPostnatal Age not TS 27, 28%s' % (CRT, CRT))
results = db.sql('''select a.accid as exptId, s._Experiment_key, s.name, s.age, t.stage
    from GXD_HTSample s, GXD_Theilerstage t, ACC_Accession a
    where s._Stage_key = t._Stage_key
    and s.age like 'postnatal%' 
    and t.stage not in (27, 28)
    and s._Experiment_key = a._Object_key
    and a._MGIType_key = 42
    and a._LogicalDB_key in (189, 190)
    and a.preferred = 1
    order by a.accID, s.name''', 'auto')

s = ''
ct = 0
for r in results:
    s = s + r['exptId'] + TAB + r['name'] + TAB + r['age'] + TAB + str(r['stage']) +  CRT
    ct += 1

fp.write('%sTotal: %s%s' % (CRT, ct, CRT))
fp.write('Experiment ID%sName%sAge%sStage%s' % (TAB, TAB, TAB, CRT))
fp.write(s)

reportlib.finish_nonps(fp)
