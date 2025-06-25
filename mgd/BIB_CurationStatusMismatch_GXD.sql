\echo ''
\echo 'References with littriage status not matching curation status'
\echo '  current GXDHT status = Done and Lit Triage GXDHT Status != Indexed'
\echo '  or'
\echo '  current GXDHT status != Done and Lit Triage GXDHT Status = Indexed'
\echo ''

(
select c.pubmedid, c.jnumid, a.accid, t1.term as curationStatus, t2.term as workflowStatus
from GXD_HTExperiment e, MGI_Property p, BIB_Citation_Cache c, BIB_Workflow_Status b, ACC_Accession a, VOC_Term t1, VOC_Term t2
where e._CurationState_key = 20475421
and e._Experiment_key = p._Object_key
and p._mgitype_key = 42
and p._propertyterm_key = 20475430
and p.value = c.pubmedid
and c._refs_key = b._refs_key
and b.isCurrent = 1
and b._Group_key = 114000000
and b._Status_key != 31576673
and e._Experiment_key = a._object_key and a._mgitype_key = 42
and a.preferred = 1
and e._CurationState_key = t1._term_key
and b._Status_key = t2._term_key
union
select c.pubmedid, c.jnumid, a.accid, t1.term, t2.term
from GXD_HTExperiment e, MGI_Property p, BIB_Citation_Cache c, BIB_Workflow_Status b, ACC_Accession a, VOC_Term t1, VOC_Term t2
where e._CurationState_key != 20475421
and e._Experiment_key = p._Object_key
and p._mgitype_key = 42
and p._propertyterm_key = 20475430
and p.value = c.pubmedid
and c._refs_key = b._refs_key
and b.isCurrent = 1
and b._Group_key = 114000000
and b._Status_key = 31576673
and e._Experiment_key = a._object_key and a._mgitype_key = 42
and a.preferred = 1
and e._CurationState_key = t1._term_key
and b._Status_key = t2._term_key
and not exists (select 1 from GXD_HTExperiment e2, MGI_Property p2, BIB_Citation_Cache c2
	where c._Refs_key = c2._Refs_key
	and e2._CurationState_key = 20475421
	and e2._Experiment_key = p2._Object_key
	and p2._mgitype_key = 42
	and p2._propertyterm_key = 20475430
	and p2.value = c2.pubmedid
	)
)
order by curationStatus, jnumid
;

