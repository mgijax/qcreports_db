
select s._Sequence_key, s._Marker_key, s.accID, c.provider
INTO TEMPORARY TABLE coord
from SEQ_Marker_Cache s, SEQ_Coord_Cache c
where s._Organism_key = 1
and s._Sequence_key = c._Sequence_key
and c.provider in ('NCBI Gene Model', 'Ensembl Gene Model', 'VEGA Gene Model')
;

create index coord_idx1 on coord(_Marker_key)
;
create index coord_idx2 on coord(provider)
;

select provider, _Marker_key
INTO TEMPORARY TABLE dups
from coord
group by provider, _Marker_key having count(*) > 1
;

create index dups_idx1 on dups(_Marker_key)
;

\echo ''
\echo 'Symbols w/ > 1 Ensembl, VEGA or NCBI Gene Model Association'
\echo ''

select m.symbol, c.accID, c.provider
from dups s, coord c, MRK_Marker m
where s._Marker_key = c._Marker_key
and s._Marker_key = m._Marker_key
order by c.provider, m.symbol
;

