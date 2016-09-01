
/* select all where the a secondary id is annotated */

select ma._Object_key, ma.accID, sa._Object_key as sequenceKey
INTO TEMPORARY TABLE markers1
from ACC_Accession sa, ACC_Accession ma
where sa._MGIType_key = 19
and sa.preferred = 0
and sa.accID = ma.accID
and ma._MGIType_key = 2
and ma._LogicalDB_key = sa._LogicalDB_key
;

create index markers1_idx1 on markers1(_Object_key)
;
create index markers1_idx2 on markers1(sequenceKey)
;

/* select all where the primary is not annotated */

select m.*
INTO TEMPORARY TABLE markers
from markers1 m
where not exists (select 1 from ACC_Accession ma, ACC_Accession sa
where m._Object_key = ma._Object_key
and ma._MGIType_key = 2
and m.sequenceKey = sa._Object_key
and sa._MGIType_key = 19
and ma.accID = sa.accID
and sa.preferred = 1)
;

create index markers_idx on markers(_Object_key)
;

select m.*, a.accID as egID
INTO TEMPORARY TABLE final
from markers m, ACC_Accession a
where m._Object_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_key = 55
union
select m.*, null
from markers m
where not exists (select 1 from ACC_Accession a
where m._Object_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_key = 55)
;

create index final_idx on final(_Object_key)
;

\echo ''
\echo 'Markers Annotated to a Secondary Sequence Accession ID'
\echo ''
\echo 'Includes: all marker statuses (official, withdrawn)'
\echo 'Includes: all marker types (gene, DNA segment, etc.)'
\echo ''

select distinct m.symbol, ma.accID, ma.egID
from final ma, MRK_Marker m
where ma._Object_key = m._Marker_key
order by ma.egID, m.symbol
;

