print ""
print "MGD Duplicate Symbols"
print ""

select _Marker_key, _Organism_key, symbol, chromosome, cytogeneticOffset
into #dup
from MRK_Marker
where _Marker_Status_key in (1,3)
group by _Organism_key, symbol, chromosome, cytogeneticOffset having count(*) > 1
go

select d._Marker_key, s.species, d.symbol, d.chromosome, d.cytogeneticOffset 
from #dup d, MRK_Species s
where d._Organism_key = s._Organism_key
go

print ""
print "MGD Duplicate Pending Markers"
print ""

select m1._Marker_key, m1.symbol, m2._Marker_key, m2.symbol
from MRK_Marker m1, MRK_Marker m2
where m1._Organism_key = 1
and m1.symbol = m2.symbol + "-pending"
and m2._Organism_key = 1
go

