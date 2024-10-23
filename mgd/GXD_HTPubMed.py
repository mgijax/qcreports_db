
'''
#
# Report:
#
# GXD HT Experiments with PMIDs that do not exist in Lit Triage
#
# PubMed ID
# Experiment ID
# Row count
#
# Usage:
#       GXD_HTPubMed.py
# 
# Notes:
#
# History:
#
# lec   10/23/2024
#   wts2-1565/e4g-39/GXD HT: Missing PMIDs
#
'''

import sys
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

fp = reportlib.init(sys.argv[0], 'GXD HT Experiments with PMIDs that do not exist in Lit Triage', os.environ['QCOUTPUTDIR'])

results = db.sql('''
    select distinct p.value, a.accid as exptId
    from GXD_HTExperiment e, ACC_Accession a, MGI_Property p
    where e._curationstate_key = 20475421 /* Done */
    and e._experiment_key = a._object_key
    and a._mgitype_key = 42 /* ht experiment type */
    and a.preferred = 1
    and e._experiment_key = p._object_key
    and p._mgitype_key = 42
    and p._propertyterm_key = 20475430
    and not exists (select 1 from BIB_Citation_Cache c where p.value = c.pubmedid)
    order by p.value
    ''', 'auto') 

for r in results:
    fp.write(r['value'] + TAB)
    fp.write(r['exptId'] + CRT)

fp.write(CRT + '(%d rows affected)' % (len(results)) + CRT)
reportlib.finish_nonps(fp)
