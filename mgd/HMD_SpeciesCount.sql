set nocount on
go

select distinct m1._Organism_key, r1._Class_key
into #organism
from HMD_Homology r1, HMD_Homology_Marker h1, 
HMD_Homology r2, HMD_Homology_Marker h2, MRK_Marker m1, MRK_Marker m2
where m1._Organism_key != 1
and m1._Marker_key = h1._Marker_key 
and h1._Homology_key = r1._Homology_key 
and r1._Class_key = r2._Class_key 
and r2._Homology_key = h2._Homology_key 
and h2._Marker_key = m2._Marker_key 
and m2._Organism_key = 1
go

select _Organism_key, organismCount = count(_Class_key) 
into #organismCount
from #organism
group by _Organism_key
go

set nocount off
go

print ""
print "Counts of Mouse Homologies by Organism"
print ""

select p.commonName, s.organismCount
from #organismCount s, MGI_Organism p
where s._Organism_key = p._Organism_key
order by s.organismCount
go

