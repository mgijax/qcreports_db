set nocount on
go

select distinct m.symbol, a.accID
into #markers
from MRK_Marker m, MRK_Acc_View a
where m._Species_key = 2
and m._Marker_key = a._Object_key
and a.prefixPart = "GDB:"
and a._LogicalDB_key = 2
go

create index index_symbol on #markers (symbol)
go

set nocount off
go

print ""
print "Human Markers with > 1 GDB record ID in LocusLink"
print ""

select m.symbol, l.locusID "LL ID", m.accID "MGD GDB ID", l.gsdbID "LL GDB ID"
from #markers m, tempdb..LL l
where m.symbol = l.osymbol
and l.taxID = 9606
and m.accID != l.gsdbID
union
select m.symbol, l.locusID, m.accID, l.gsdbID
from #markers m, tempdb..LL l
where m.symbol = l.isymbol
and l.taxID = 9606
and m.accID != l.gsdbID
order by m.symbol
go
