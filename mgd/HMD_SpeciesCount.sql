set nocount on
go

select m1._Species_key, speciesCount = count(distinct r1._Class_key) 
into #species
from HMD_Homology r1, HMD_Homology_Marker h1, 
HMD_Homology r2, HMD_Homology_Marker h2, MRK_Marker m1, MRK_Marker m2
where m1._Species_key > 1
and m1._Marker_key = h1._Marker_key 
and h1._Homology_key = r1._Homology_key 
and r1._Class_key = r2._Class_key 
and r2._Homology_key = h2._Homology_key 
and h2._Marker_key = m2._Marker_key 
and m2._Species_key = 1
group by m1._Species_key
go

set nocount off
go

print ""
print "Counts of Mouse Homologies by Species"
print ""

select p.name, s.speciesCount
from #species s, MRK_Species p
where s._Species_key = p._Species_key
order by s.speciesCount
go

