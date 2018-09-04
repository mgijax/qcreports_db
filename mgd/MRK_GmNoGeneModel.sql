
select distinct m._Marker_key, a.accID, m.symbol, m.name
INTO TEMPORARY TABLE markers
from MRK_Marker m, ACC_Accession a
where m._Organism_key = 1
and m._Marker_Status_key = 1
and m.name like 'predicted gene%'
and not exists (select 1 from SEQ_Marker_Cache c
where m._Marker_key = c._Marker_key
and c._LogicalDB_key in (59,60))
and m._Marker_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_Key = 1
and a.prefixPart = 'MGI:'
and a.preferred = 1
;

select m._Marker_key, hm.symbol, substring(h.name,1,50) as name
INTO TEMPORARY TABLE history
from markers m, MRK_History h, MRK_Marker hm
where m._Marker_key = h._Marker_key
and m.name != h.name
and h._History_key = hm._Marker_key
and m.symbol != hm.symbol
;

\echo ''
\echo 'Gm Markers without Gene Model Associations'
\echo ''
\echo '   where name begins ''predicted gene'''
\echo '   and status = ''official'' '
\echo ''

(
select m.accID, m.symbol, h.symbol as "old symbol", h.name
from markers m, history h
where m._Marker_key = h._Marker_key
union
select m.accID, m.symbol, null, null
from markers m
where not exists (select 1 from history h where m._Marker_key = h._Marker_key)
)
order by symbol
;

