'''
#
# GXD HT Experiment To Do List with PMIDs
#
# a list of HT Experiments where Curation State=Not Done, Evaluation in (Yes,Maybe)
#
# Column 1: PubMed ID
# Column 2: In MGI? (yes/no re is it in MasterBib; if easier, the existing “PubMed Id in/not in MGI” custom report returns relevanceterm.
# Column 3: Experiment ID (primary)
# Column 4: Evaluation
#
# Sort:
# Primary: Column 2 (in MGI?) (A->Z)
# Secondary Sort: Column 4 (Evaluation) (Z->A)
# Tertiary: Column 1 (PubMed ID)
# Quarternary: Column 3 (Experiment ID)
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
    sys.stdout.write('PubMed ID' + TAB)
    sys.stdout.write('In MGI?' + TAB)
    sys.stdout.write('Experiment ID' + TAB)
    sys.stdout.write('Evaluation' + CRT)

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
    -- PubMed ID, in MGI
    select e.*, p.value as pubmedid, 'yes' as inMGI
    from eresults e, mgi_property p
    where e._experiment_key = p._object_key
    and p._propertytype_key = 1002
    and p._propertyterm_key = 20475430
    and exists (select 1 from bib_citation_cache c where p.value = c.pubmedid)
    union
    select e.*, p.value as pubmedid, 'no' as inMGI
    from eresults e, mgi_property p
    where e._experiment_key = p._object_key
    and p._propertytype_key = 1002
    and p._propertyterm_key = 20475430
    and not exists (select 1 from bib_citation_cache c where p.value = c.pubmedid)
    )
    order by inMGI, evaluationState desc, pubmedid, experimentID
    ''', 'auto')

    for r in results:
            sys.stdout.write(r['pubmedid'] + TAB)
            sys.stdout.write(r['inMGI'] + TAB)
            sys.stdout.write(r['experimentID'] + TAB)
            sys.stdout.write(r['evaluationState'] + CRT)

    sys.stdout.flush()

