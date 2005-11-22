print ""
print "Markers which contain Alleles which do not match the Marker Symbol"
print ""

select m.symbol "Marker", a.symbol "Allele"
from ALL_Allele a, MRK_Marker m
where a._Marker_key = m._Marker_key
and a.symbol != "+"
and a.symbol not like "%" + m.symbol + "%"
go

set nocount on
go

select _Allele_key
into #duplicates
from ALL_Allele
where symbol != "+"
group by symbol having count(*) > 1
go

set nocount off
go

print ""
print "Duplicate Allele Symbols"
print ""

select a.symbol, a.markerSymbol
from #duplicates d, ALL_Allele_View a
where d._Allele_key = a._Allele_key
order by markerSymbol
go

