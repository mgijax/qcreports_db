print ""
print "Markers and Alleles"
print ""

select distinct m.symbol "Symbol", m.chromosome "Chr", Allele = a.symbol
from MRK_Marker m, ALL_Allele a
where m._Species_key = 1
and m._Marker_key = a._Marker_key
order by m.symbol, Allele
go

