set nocount on
go

select distinct m._Marker_key, a.accID
into #markers
from MRK_Marker m, MRK_Acc_View a
where m._Species_key = 2
and m._Marker_key = a._Object_key
and a.prefixPart = "GDB:"
and a._LogicalDB_key = 2
go

select *
into #dups
from #markers
group by _Marker_key having count(*) > 1
go

set nocount off
go

print ""
print "Human Markers with > 1 GDB record ID"
print ""

select m.symbol, a.accID "LL ID", d.accID "GDB ID"
from #dups d, MRK_Marker m, MRK_Acc_View a
where d._Marker_key = m._Marker_key
and d._Marker_key = a._Object_key
and a._LogicalDB_key = 24
order by m.symbol
go
