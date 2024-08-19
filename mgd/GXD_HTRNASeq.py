
'''
#
# Report:
#
# GXD HT Experiment Type = RNA-Seq 
# GXD HT Curation State = Done
# and experiment is not annotationed to any of the following GXD HT Experimental Variables:
#   bulk RNA-seq : bulk RNA-seq
#   single cell RNA-seq : scRNA-seq
#   spatial RNA-seq : spatial seq
#
# Experiment ID
# Row count
#
# Usage:
#       GXD_HTRNASeq.py
# 
# Notes:
#
# History:
#
# lec   08/19/2024
#   fl2-950/wts2-1536
#
'''

import sys
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

fp = reportlib.init(sys.argv[0], 'RNA seq experiments missing needed experimental variable', os.environ['QCOUTPUTDIR'])

results = db.sql('''
    select a.accid as exptId
    from GXD_HTExperiment e, ACC_Accession a
    where e._ExperimentType_key = 20475437
    and e._CurationState_key = 20475421
    and e._Experiment_key = a._Object_key
    and a._MGIType_key = 42
    and a._LogicalDB_key in (189, 190)
    and a.preferred = 1 
    and not exists (select 1 from GXD_HTExperimentVariable v where e._Experiment_key = v._Experiment_key and v._Term_key = 114732569)
    and not exists (select 1 from GXD_HTExperimentVariable v where e._Experiment_key = v._Experiment_key and v._Term_key = 114732570)
    and not exists (select 1 from GXD_HTExperimentVariable v where e._Experiment_key = v._Experiment_key and v._Term_key = 114732571)
    order by a.accid
    ''', 'auto') 

for r in results:
    fp.write(r['exptId'] + CRT)

fp.write(CRT + '(%d rows affected)' % (len(results)) + CRT)
reportlib.finish_nonps(fp)
