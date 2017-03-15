select a.accID, a._Object_key, t.term 
INTO TEMPORARY TABLE obsolete 
from VOC_Term_ACC_View a, VOC_Term t 
where t._Vocab_key = 125
and t.isObsolete = 1 
and t._Term_key = a._Object_key
and a._LogicalDB_key = 191
and a.preferred = 1
;

create index idx_key on obsolete(_Object_key)
;

\echo ''
\echo 'Genotype Annotations to Obsolete DO Terms'
\echo ''

select g.accID as "Genotype ID", o.accID as "DO ID", substring(o.term , 1, 100) as "Term"
from obsolete o, VOC_Annot a, ACC_Accession g
where a._AnnotType_key = 1020 
and a._Term_key = o._Object_key 
and a._Object_key = g._Object_key 
and g._MGIType_key = 12
and g._LogicalDB_key = 1 
and g.prefixPart = 'MGI:' 
and g.preferred = 1
;

