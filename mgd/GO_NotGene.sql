
select v._Object_key, substring(m.name,1,50) as name, m.symbol, m._Marker_Type_key
INTO TEMPORARY TABLE nongene
from VOC_Annot v, MRK_Marker m
where v._AnnotType_key = 1000
and v._Object_key = m._Marker_key
and m._Marker_Type_key != 1
;

create index nongene_idx1 on nongene(_Object_key)
;

select _Object_key, count(_Object_key) as annotations
INTO TEMPORARY TABLE nongeneout
from nongene 
group by _Object_key
;

create index nongeneout_idx on nongeneout(_Object_key)
;

select distinct a.accID, substring(t.name,1,25) as type, g.symbol, g.name, m.annotations
INTO TEMPORARY TABLE toPrint
from nongeneout m, nongene g, ACC_Accession a, MRK_Types t
where m._Object_key = g._Object_key
and g._Marker_Type_key = t._Marker_Type_key
and m._Object_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_key = 1
and a.prefixPart = 'MGI:'
and a.preferred = 1
;

\echo ''
\echo 'Non-Gene Markers with GO Annotations'
\echo ''

select 'Number of unique MGI Gene IDs:  ', count(distinct accID) from toPrint
union
select 'Number of total rows:  ', count(*) from toPrint
;

\echo ''

select * from toPrint order by name
;

