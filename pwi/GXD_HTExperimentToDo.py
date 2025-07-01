'''
#
# GXD HT Experiment To Do List
#
# a list of HT Experiments where Curation State=Not Done, Evaluation in (Yes,Maybe)
#
# Column 1: Experiment ID
# Column 2: PubMed ID (if present)
# Column 3: Evaluation
# Column 4: Experiment note (if present)
#
# Sort:
# Primary: Column 3 (evaluation) Z->A
# Secondary: Column 4 (experiment note) (A->Z)
# Tertiary: Column 2 (PMID) (A->Z)
# Quaternary: Column 1 (ExpID) (A->Z)
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
    #
    # Main
    #

    # Write header
    sys.stdout.write('Experiment ID (primary)' + TAB)
    sys.stdout.write('PubMed ID' + TAB)
    sys.stdout.write('Evaluation' + TAB)
    sys.stdout.write('Experiment note' + CRT)

    results = db.sql('''
    WITH eresults AS (
    select e._experiment_key,
    a.accid as experimentID, 
    t1.term as evaluationState, 
    t2.term as curationState
    from gxd_htexperiment e, voc_term t1, voc_term t2, acc_accession a
    where e._evaluationstate_key = t1._term_key 
    and e._curationstate_key = t2._term_key 
    and e._experiment_key = a._object_key 
    and a._mgitype_key = 42 
    and a._logicaldb_key in (189,190) 
    and a.preferred = 1 
    and t1.term in ('Yes', 'Maybe')
    and t2.term = 'Not Done'
    )
    (
    -- PubMed ID, Note
    select e.*, n.note, p.value as pubmedid
    from eresults e, mgi_property p, mgi_note n
    where e._experiment_key = p._object_key
    and p._propertytype_key = 1002
    and p._propertyterm_key = 20475430
    and e._experiment_key = n._object_key 
    and n._notetype_key = 1047 
    union
    -- PubMed ID, no Note
    select e.*, null as note, p.value as pubmedid
    from eresults e, mgi_property p
    where e._experiment_key = p._object_key
    and p._propertytype_key = 1002
    and p._propertyterm_key = 20475430
    and not exists (select 1 from mgi_note n
        where e._experiment_key = n._object_key 
        and n._notetype_key = 1047 
        )
    union
    -- no PubMed ID, Note
    select e.*, n.note as note, null
    from eresults e, mgi_note n
    where e._experiment_key = n._object_key 
    and n._notetype_key = 1047 
    and not exists (select 1 from mgi_property p
        where e._experiment_key = p._object_key
        and p._propertytype_key = 1002
        and p._propertyterm_key = 20475430
        )
    union
    -- no PubMed ID, no Note
    select e.*, null, null
    from eresults e
    where not exists (select 1 from mgi_property p
        where e._experiment_key = p._object_key
        and p._propertytype_key = 1002
        and p._propertyterm_key = 20475430
        )
    and not exists (select 1 from mgi_note n
        where e._experiment_key = n._object_key 
        and n._notetype_key = 1047 
        )
    )
    order by evaluationState desc, note, pubmedid, experimentID
    ''', 'auto')

    for r in results:
            sys.stdout.write(r['experimentID'] + TAB)

            try:
                sys.stdout.write(r['pubmedid'] + TAB)
            except:
                sys.stdout.write(TAB)

            sys.stdout.write(r['evaluationState'] + TAB)

            try:
                note = r['note'].replace('\n', ' ').replace('\t', ' ')
            except:
                note = ""
            sys.stdout.write(note + CRT)

    sys.stdout.flush()

