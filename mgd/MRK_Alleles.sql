print ""
print "Markers which contain Alleles with Proposed Names"
print ""

select distinct m.symbol "Symbol", m.chromosome "Chr", a.symbol "Allele",
substring(a.name, 1, 40) "Name"
from MRK_Marker m, ALL_Allele a
where m._Organism_key = 1
and m._Marker_key = a._Marker_key
and a.name = 'allele name in progress'
order by m.symbol
go

print ""
print "Markers which contain Alleles which do not match the Marker Symbol"
print ""

select m.symbol "Marker", a.symbol "Allele"
from ALL_Allele a, MRK_Marker m
where a._Marker_key = m._Marker_key
and a.symbol not like m.symbol + "%"
go

set nocount on
go

select _Allele_key
into #duplicates
from ALL_Allele
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

set nocount on
go

select m2._Marker_key, m2.symbol, _Allele_key = m1._Marker_key, allele = m1.symbol
into #alleles
from MRK_Current c, MRK_Marker m1, MRK_Marker m2
where m1._Marker_Status_key = 2
and m1.name like '%allele of%'
and m1._Marker_key = c._Marker_key
and c._Current_key = m2._Marker_key
go

set nocount off
go

print ""
print "Withdrawn Allele Markers not found in Allele Table"
print ""

select m.symbol "Marker Symbol", m.allele "Allele Symbol"
from #alleles m
where not exists (select * from ALL_Allele a where
m._Marker_key = a._Marker_key
and a.symbol like m.symbol + "%<" + m.allele + "%>")
order by m.symbol
go

