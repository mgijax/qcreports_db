
\echo ''
\echo 'DO terms not in the DO slim'
\echo ''

WITH inslimset AS (
select tt._Term_key as childkey, tt.term, t._Term_key, t.term
from VOC_Term tt, DAG_Closure dc, VOC_Term t
where tt._Vocab_key = 125 
and tt._Term_key = dc._DescendentObject_key
and dc._AncestorObject_key = t._Term_key
and exists (select 1 from MGI_SetMember s
        where t._Term_key = s._Object_key
        and s._Set_key = 1048)
)
select tt.term as childTerm, t.term as parentTerm
from VOC_Term tt, DAG_Closure dc, VOC_Term t
where tt._Vocab_key = 125 
and tt._Term_key = dc._DescendentObject_key
and dc._AncestorObject_key = t._Term_key
-- the child does not exist in the slim set 
and not exists (select 1 from inslimset s where tt._Term_key = s.childkey)
and exists (select 1 from VOC_Annot va  
        where tt._Term_key = va._Term_key
        and va._AnnotType_key in (1020, 1022)
        )
order by childTerm, parentTerm
;

