
set nocount on
go

select s._Sequence_key, s._Marker_key, s.accID, c.provider
into #coord
from SEQ_Marker_Cache s, SEQ_Coord_Cache c
where s._Organism_key = 1
and s._Sequence_key = c._Sequence_key
and c.provider in ('Ensembl Gene Model', 'VEGA Gene Model', 'NCBI Gene Model')
go

create index coord_idx1 on #coord(_Sequence_key)
go
create index coord_idx2 on #coord(provider)
go

select provider, _Sequence_key
into #dups
from #coord
group by provider, _Sequence_key having count(*) > 1
go

create index dups_idx1 on #dups(_Sequence_key)
go

set nocount off
go

print ''
print 'Ensembl, VEGA Gene Models, or NCBI Gene Model w/ > 1 Marker Association'
print ''

select c.accID, m.symbol, c.provider
from #dups s, #coord c, MRK_Marker m
where s._Sequence_key = c._Sequence_key
and c._Marker_key = m._marker_key
order by c.provider, c.accID
go

drop table #coord
go
drop table #dups
go

