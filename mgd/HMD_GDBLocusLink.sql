set nocount on
go

select distinct m.symbol, a.accID
into #markers
from MRK_Marker m, ACC_Accession a
where m._Organism_key = 2
and m._Marker_key = a._Object_key
and a._MGIType_key = 2
and a.prefixPart = "GDB:"
and a._LogicalDB_key = 2
go

set nocount off
go

print ""
print "Human Markers with > 1 GDB record ID in LocusLink"
print ""

select m.symbol, l.locusID "LL ID", m.accID "MGD GDB ID", l.gsdbID "LL GDB ID"
from #markers m, radar..DP_LL l
where m.symbol = l.osymbol
and l.taxID = 9606
and m.accID != l.gsdbID
union
select m.symbol, l.locusID, m.accID, l.gsdbID
from #markers m, radar..DP_LL l
where m.symbol = l.isymbol
and l.taxID = 9606
and m.accID != l.gsdbID
order by m.symbol
go
