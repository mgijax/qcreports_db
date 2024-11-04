
'''
#
# Report:
#
# GXD HT Experiments #8
# RNA-Seq Samples missing RNA-Seq Type
#
# Experiment type = RNA Seq
# GXD relevance = Yes
# RNA-Seq Type value = “Not Specified”
# 
# Columns - 1: Experiment ID  2: Sample Name
# Sort order – Experiment ID
#
# History:
#
# lec   11/01/2024
#   wts2-1539/e4g-57/GXD RNA-Seq Type/Schema/Migration
#
'''

import sys
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

fp = reportlib.init(sys.argv[0], 'RNA-Seq Samples missing RNA-Seq Type', os.environ['QCOUTPUTDIR'])

#    select a.accid, array_to_string(array_agg(distinct s.name),'|') as name
#    group by accid
results = db.sql('''
    select a.accid, s.name
    from GXD_HTExperiment e, ACC_Accession a, GXD_HTSample s
    where e._experimenttype_key = 20475437
    and e._experiment_key = s._experiment_key
    and s._rnaseqtype_key in (114866227,114866228)
    and e._experiment_key = a._object_key
    and a._logicaldb_key in (189,190)
    order by accid
    ''', 'auto') 
for r in results:
    fp.write(r['accid'] + TAB)
    fp.write(r['name'] + CRT)
fp.write(CRT + '(%d rows affected)' % (len(results)) + CRT)

reportlib.finish_nonps(fp)
