
select s._Sequence_key, s._Marker_key, s.accID, c.provider
INTO TEMPORARY TABLE coord
from SEQ_Marker_Cache s, SEQ_Coord_Cache c
where s._Organism_key = 1
and s._Sequence_key = c._Sequence_key
and c.provider in ('Ensembl Gene Model', 'NCBI Gene Model')
;

create index coord_idx1 on coord(_Sequence_key)
;
create index coord_idx2 on coord(provider)
;

select provider, _Sequence_key
INTO TEMPORARY TABLE dups
from coord
group by provider, _Sequence_key having count(*) > 1
;

create index dups_idx1 on dups(_Sequence_key)
;

\echo ''
\echo 'Ensembl, NCBI Gene Model w/ > 1 Marker Association'
\echo ''

select c.accID, m.symbol, c.provider
from dups s, coord c, MRK_Marker m
where s._Sequence_key = c._Sequence_key
and c._Marker_key = m._marker_key
order by c.provider, c.accID
;

