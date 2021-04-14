
--
-- select duplicate DO/Allele annotations
--

\echo ''
\echo 'Duplicate DO/Allele Annotations'
\echo ''

select a.accid as genoID, vav.accid as doID, vev.jnumid
from voc_annot_view vav, voc_evidence_view vev, acc_accession a
where vav._annottype_key = 1021
and vav._annot_key = vev._annot_key
and vav._object_key = a._object_key
and a._mgitype_key = 11
and a._logicaldb_key = 1
and a.preferred = 1
and a.prefixPart = 'MGI:'
group by a.accid, vav._object_key, vav.accid, vev.jnumid
having count(*) >1
order by a.accid

;

\echo ''
\echo 'Duplicate DO/Genotype Annotations'
\echo ''

select a.accid as genoID, vav.accid as doID, vev.jnumid
from voc_annot_view vav, voc_evidence_view vev, acc_accession a
where vav._annottype_key = 1020
and vav._annot_key = vev._annot_key
and vav._object_key = a._object_key
and a._mgitype_key = 12
and a._logicaldb_key = 1
and a.preferred = 1
and a.prefixPart = 'MGI:'
group by a.accid, vav._object_key, vav.accid, vev.jnumid
having count(*) >1
order by a.accid
;

