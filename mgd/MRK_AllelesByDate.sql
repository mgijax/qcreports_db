print ""
print "Markers Which Contain Alleles (By Modification Date)"
print ""

select distinct m.symbol "Symbol", a.symbol "Allele", substring(a.name, 1, 40) "Allele Name",
convert(char(10), m.modification_date, 101) "Modification Date"
from MRK_Marker m, ALL_Allele a
where m._Species_key = 1
and m._Marker_key = a._Marker_key
order by m.modification_date desc, m.symbol
go

