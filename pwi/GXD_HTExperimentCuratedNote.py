
'''
#
# GXD HT Experiment Notes for Curated Experiments
#
# This report would display 
#
# Report name: GXD HT Experiment Notes for Curated Experiments
#       Experiment ID
#       Note
#
'''
 
import sys
import os
import db
import reportlib

#db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

def go (form) :
    results = db.sql('''
    select e._experiment_key,
    a.accid as ExperimentID, 
    n.note
    from gxd_htexperiment e, acc_accession a, mgi_note n
    where e._experiment_key = a._object_key 
    and a._mgitype_key = 42 
    and a._logicaldb_key in (189,190) 
    and a.preferred = 1 
    and e._curationstate_key = 20475421
    and e._experiment_key = n._object_key 
    and n._notetype_key = 1047 
    order by note
    ''')

    sys.stdout.write('ExperimentID' + TAB)
    sys.stdout.write('note' + CRT)

    for r in results:
            sys.stdout.write(r['ExperimentID'] + TAB)
            note = r['note'].replace('\n', ' ').replace('\t', ' ')
            sys.stdout.write(note + CRT)

    sys.stdout.flush()

