
--
-- select duplicate MP annotations
--

select a._Term_key, a._Object_key, a._Qualifier_key, e._EvidenceTerm_key, e._Refs_key, p.value as sexvalue
INTO TEMPORARY TABLE a
from VOC_Annot a, VOC_Evidence e, VOC_Evidence_Property p, VOC_Term t
where a._AnnotType_key = 1002
and a._Annot_key = e._Annot_key
and e._AnnotEvidence_key = p._AnnotEvidence_key
and p._PropertyTerm_key = t._Term_key
and t._Vocab_key = 86 
and t._Term_key = 8836535
;

select a.*
INTO TEMPORARY TABLE dup
from a a
group by _Term_key, _Object_key, _Qualifier_key, _EvidenceTerm_key, _Refs_key, sexvalue
having count(*) > 1
;

\echo ''
\echo 'Duplicate MP Annotations'
\echo ''

select a.accID, ta.accID, substring(t.term,1,50) as term, d.sexvalue
from dup d, ACC_Accession a, ACC_Accession ta, VOC_Term t
where d._Object_key = a._Object_key
and a._MGIType_key = 12
and d._Term_key = ta._Object_key
and ta._MGIType_key = 13
and ta.preferred = 1
and d._Term_key = t._Term_key
order by ta.accID
;

