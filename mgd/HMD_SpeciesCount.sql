set nocount on
go

select distinct h1._Organism_key, h1._Class_key
into #organism
from MRK_Homology_Cache h1, MRK_Homology_Cache h2
where h1._Organism_key != 1
and h1._Class_key = h2._Class_key 
and h2._Organism_key = 1
go

select _Organism_key, organismCount = count(_Class_key) 
into #organismCount
from #organism
group by _Organism_key
go

set nocount off
go

print ""
print "Counts of Mouse Orthologies by Organism"
print ""

select p.commonName, s.organismCount
from #organismCount s, MGI_Organism p
where s._Organism_key = p._Organism_key
order by s.organismCount
go

