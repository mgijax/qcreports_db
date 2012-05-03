
set nocount on
go

select s._Sequence_key, s._Marker_key, s.accID, c.provider
into #coord
from SEQ_Marker_Cache s, SEQ_Coord_Cache c
where s._Organism_key = 1
and s._Sequence_key = c._Sequence_key
and c.provider in ('Ensembl Gene Model', 'VEGA Gene Model', 'NCBI Gene Model')
go

create index idx1 on #coord(_Sequence_key)
create index idx2 on #coord(provider)
go

select _Sequence_key, _Marker_key, accID, provider
into #dups
from #coord
group by provider, _Sequence_key having count(*) > 1
go

create index idx1 on #dups(_Marker_key)
create index idx2 on #dups(_Sequence_key)
go

set nocount off
go

print ''
print 'Ensembl, VEGA Gene Models, or NCBI Gene Model w/ > 1 Marker Association'
print ''

select s.accID, m.symbol, substring(s.provider,1,40) as provider
from #dups s, MRK_Marker m
where s._Marker_key = m._Marker_key
order by s.provider, s.accID
go


