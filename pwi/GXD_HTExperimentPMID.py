
'''
#
# GXD HT Experiment Partially Reviewed Papers
#
# -- Raw Experimental Factor 
# -- Raw Experiment Type 
# -- Raw Contact Name (Provider) 
# -- PubMed ID
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
    WITH pubmedids as (
    select distinct p.value as pmid
    from GXD_HTExperiment hte, MGI_Property p
    where hte._Experiment_key = p._Object_key
    and p._PropertyType_key = 1002  -- GXD HT Experiment
    and p._propertyterm_key = 20475430 -- PubMed ID
    and p._mgitype_key = 42 -- GXD HT Experiment
    )
    select pubmedids.pmid, a1.accid as expID,
        hte.name as title,
        t2.term as evaluationState,
        t3.term as curationState,
        t1.term as propertyName
    from pubmedids,
         MGI_Property p,
         GXD_HTExperiment hte,
         VOC_Term t1,
         VOC_Term t2,
         VOC_Term t3,
         ACC_Accession a1
    where pubmedids.pmid = p.value
    and p._PropertyType_key = 1002  -- GXD HT Experiment
    and p._propertyterm_key = 20475430 -- PubMed ID
    and p._PropertyTerm_key = t1._Term_key
    and p._mgitype_key = 42 -- GXD HT Experiment
    and  p._Object_key = hte._Experiment_key
    and hte._evaluationstate_key in (99646147,99646148)  -- Predicted Yes, Predicted No
    and hte._evaluationstate_key = t2._term_key
    and hte._curationstate_key = t3._term_key
    and hte._Experiment_key = a1._Object_key
    and a1._MGIType_key = 42 -- GXD HT Experiment
    and a1.preferred = 1
    and a1._LogicalDB_key in (189,190) --arrayExp, geo
    order by t2.term, length(a1.accid), a1.accid, pubmedids.pmid
    ''', 'auto')

    sys.stdout.write('expID' + TAB)
    sys.stdout.write('title' + TAB)
    sys.stdout.write('evaluationState' + TAB)
    sys.stdout.write('curationState' + TAB)
    sys.stdout.write('PubMedID' + CRT)

    for r in results:
            sys.stdout.write(r['expID'] + TAB)
            sys.stdout.write(r['title'] + TAB)
            sys.stdout.write(r['evaluationState'] + TAB)
            sys.stdout.write(r['curationState'] + TAB)
            sys.stdout.write(r['pmid'] + CRT)

    sys.stdout.flush()

