
set nocount on
go

select distinct m._Marker_key, a.accID, m.symbol, m.name
into #markers
from MRK_Marker m, ACC_Accession a
where m._Organism_key = 1
and m._Marker_Status_key in (1,3)
and m.name like 'predicted gene%'
and not exists (select 1 from SEQ_Marker_Cache c
where m._Marker_key = c._Marker_key
and c._LogicalDB_key in (59,60,85))
and m._Marker_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_Key = 1
and a.prefixPart = 'MGI:'
and a.preferred = 1
go

select m._Marker_key, hm.symbol, substring(h.name,1,50) as name
into #history
from #markers m, MRK_History h, MRK_Marker hm
where m._Marker_key = h._Marker_key
and m.name != h.name
and h._History_key = hm._Marker_key
and m.symbol != hm.symbol
go

set nocount off
go

print ''
print 'Gm Markers without Gene Model Associations'
print ''
print '   where name begins 'predicted gene''
print '   and status = 'official' or 'interim''
print ''

select m.accID, m.symbol, h.symbol as "old symbol", h.name
from #markers m, #history h
where m._Marker_key = h._Marker_key
union
select m.accID, m.symbol, null, null
from #markers m
where not exists (select 1 from #history h where m._Marker_key = h._Marker_key)
order by m.symbol
go

drop table #markers
drop table #history
go
