set nocount on
go

select distinct hm1._Marker_key, m.symbol, h1._Class_key
into #homology
from HMD_Homology h1, HMD_Homology_Marker hm1,
HMD_Homology h2, HMD_Homology_Marker hm2, MRK_Marker m
where h1._Homology_key = hm1._Homology_key
and hm1._Marker_key = hm2._Marker_key
and hm2._Homology_key = h2._Homology_key
and h1._Class_key != h2._Class_key
and hm1._Marker_key = m._Marker_key
go
 
set nocount off
go

print ""
print "Duplicate Homologies By Class"
print ""

select v._Marker_key, v.symbol, substring(v.commonName,1,25), v.jnum, v._Class_key
from #homology h, HMD_Homology_View v
where h._Class_key = v._Class_key
order by v._Class_key, v._Marker_key
go

set nocount on
go

drop table #homology
go

select distinct r._Class_key, m._Species_key, m.symbol
into #homology
from HMD_Homology r, HMD_Homology_Marker h, MRK_Marker m
where r._Homology_key = h._Homology_key
and h._Marker_key = m._Marker_key
go

select distinct _Class_key
into #duplicates
from #homology
group by _Class_key, _Species_key having count(*) > 1
go

set nocount off
go

print ""
print "Duplicate Homologies By Species"
print ""

select distinct h.symbol, substring(h.commonName,1,25), h.jnum, h._Class_key 
from HMD_Homology_View h, #duplicates d
where d._Class_key = h._Class_key
order by h._Class_key, h.species
go

