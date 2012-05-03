
set nocount on
go

select s._Sequence_key, s._Marker_key, s.accID, c.provider
into #coord
from SEQ_Marker_Cache s, SEQ_Coord_Cache c
where s._Organism_key = 1
and s._Sequence_key = c._Sequence_key
and c.provider in ('NCBI Gene Model', 'Ensembl Gene Model', 'VEGA Gene Model')
go

create index idx1 on #coord(_Marker_key)
create index idx2 on #coord(provider)
go

select _Sequence_key, _Marker_key, accID, provider
into #dups
from #coord
group by provider, _Marker_key having count(*) > 1
go

create index idx1 on #dups(_Marker_key)
create index idx2 on #dups(_Sequence_key)
go

set nocount off
go

print ''
print 'Symbols w/ > 1 Ensembl, VEGA or NCBI Gene Model Association'
print ''

select m.symbol, s.accID, substring(s.provider,1,50) as provider
from #dups s, MRK_Marker m
where s._Marker_key = m._Marker_key
order by s.provider, m.symbol
go

drop table #coord
go
drop table #dups
go
