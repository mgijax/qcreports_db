\echo ''
\echo 'GXD Results & Cre that contains obsolete CL terms'
\echo ''

select distinct bc.jnumid, ga.accid, s.specimenlabel, t.term, va.accid
from GXD_Assay a, GXD_Specimen s, GXD_InSituResult r, GXD_ISResultCellType c, VOC_Term t,
        BIB_Citation_Cache bc, ACC_Accession ga, ACC_Accession va
where a._assay_key = s._assay_key
and s._specimen_key = r._specimen_key
and r._result_key = c._result_key
and c._celltype_term_key = t._term_key
and t._Vocab_key = 102
and t.isObsolete = 1
and a._refs_key = bc._refs_key
and a._assay_key = ga._object_key
and ga._mgitype_key = 8
and ga._logicaldb_key = 1
and c._celltype_term_key = va._object_key
and va._mgitype_key = 13
and va.preferred = 1
order by term
;

\echo ''
\echo 'GXD HT Indexing that contains obsolete CL terms'
\echo ''

select distinct ga.accid, c.name, t.term, va.accid
from GXD_HTExperiment a, GXD_HTSample c, VOC_Term t, ACC_Accession ga, ACC_Accession va
where a._experiment_key = c._experiment_key
and c._celltype_term_key = t._term_key
and t._Vocab_key = 102
and t.isObsolete = 1
and a._experiment_key = ga._object_key
and ga._mgitype_key = 42
and c._celltype_term_key = va._object_key
and va._mgitype_key = 13
and va.preferred = 1
order by term
;

