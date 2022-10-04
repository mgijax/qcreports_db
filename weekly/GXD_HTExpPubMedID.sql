\echo ''
\echo 'HT Experiments with PMIDs used by GXD'
\echo 'sort:  Experiment Type, Evaluation State (desc), Curation State (desc), Experiment ID'
\echo ''

select a.accid as ExperimentID, c.jnumid, p.value, t.term as evaluationstate, t3.term as curationstate, t2.term as experimenttype, e.name
from gxd_htexperiment e, voc_term t, voc_term t2, voc_term t3, acc_accession a, mgi_property p, bib_citation_cache c
where e._evaluationstate_key = t._term_key
and e._experimenttype_key = t2._term_key
and e._curationstate_key = t3._term_key
and e._experiment_key = a._object_key
and a._mgitype_key = 42
and a._logicaldb_key in (189,190)
and a.preferred = 1
and p._propertytype_key = 1002 
and p._propertyterm_key = 20475430      -- PubMed ID
and e._experiment_key = p._object_key
and p.value = c.pubmedid
and exists (select 1 from bib_workflow_status s
        where c._refs_key = s._refs_key
        and s.isCurrent = 1
        and s._group_key = 31576665
        and s._status_key in (31576671, 31576674, 31576673)
        )
order by t2.term, t.term desc, t3.term desc, a.accid

