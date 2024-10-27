
'''
#
# Report:
#
# GXD HT Experiments with PMIDs that do not exist in Lit Triage
# GXD HT Experiments with PMIDs that exist in Lit Triage but do not have J:
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

#fp = reportlib.init(sys.argv[0], 'Curated GXD HT Experiments with PMIDs that do not exist in Lit Triage', os.environ['QCOUTPUTDIR'])
fp = reportlib.init(sys.argv[0], 'Curated GXD HT Experiments with PMIDs Issues', os.environ['QCOUTPUTDIR'])

fp.write('\nCurated GXD HT Experiments with PMIDs that do not exist in Lit Triage\n\n')
results = db.sql('''
    select distinct p.value, array_to_string(array_agg(distinct a.accid),'|') as exptId
    from GXD_HTExperiment e, ACC_Accession a, MGI_Property p
    where e._curationstate_key = 20475421 /* Done */
    and e._experiment_key = a._object_key
    and a._mgitype_key = 42 /* ht experiment type */
    and a.preferred = 1
    and e._experiment_key = p._object_key
    and p._mgitype_key = 42
    and p._propertyterm_key = 20475430
    and not exists (select 1 from BIB_Citation_Cache c where p.value = c.pubmedid)
    group by p.value
    order by value
    ''', 'auto') 
for r in results:
    fp.write(r['value'] + TAB)
    fp.write(r['exptId'] + CRT)
fp.write(CRT + '(%d rows affected)' % (len(results)) + CRT)

fp.write('\nCurated GXD HT Experiments with PMIDs that exist in Lit Triage but do not have a J:\n\n')
results = db.sql('''
    select distinct p.value, array_to_string(array_agg(distinct a.accid),'|') as exptId
    from GXD_HTExperiment e, ACC_Accession a, MGI_Property p
    where e._curationstate_key = 20475421 /* Done */
    and e._experiment_key = a._object_key
    and a._mgitype_key = 42 /* ht experiment type */
    and a.preferred = 1
    and e._experiment_key = p._object_key
    and p._mgitype_key = 42
    and p._propertyterm_key = 20475430
    and exists (select 1 from BIB_Citation_Cache c where p.value = c.pubmedid and c.jnumid is null)
    group by p.value
    order by value
    ''', 'auto') 
for r in results:
    fp.write(r['value'] + TAB)
    fp.write(r['exptId'] + CRT)
fp.write(CRT + '(%d rows affected)' % (len(results)) + CRT)

reportlib.finish_nonps(fp)
