print ""
print "Duplicate Pending Markers"
print ""

select m1._Marker_key, m1.symbol, m2._Marker_key, m2.symbol
from MRK_Marker m1, MRK_Marker m2
where m1._Species_key = 1
and m1.symbol = m2.symbol + "-pending"
and m2._Species_key = 1
go

print ""
print "Duplicate Markers For Other Species"
print ""

select _Marker_key, _Species_key, symbol, chromosome, cytogeneticOffset from MRK_Marker
where _Species_key != 1
group by _Species_key, symbol having count(*) > 1
go

