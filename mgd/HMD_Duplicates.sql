set nocount on
go

select distinct hm1._Marker_key, m.symbol, hm1._Class_key
into #homology
from MRK_Homology_Cache hm1, MRK_Homology_Cache hm2, MRK_Marker m
where hm1._Marker_key = hm2._Marker_key
and hm1._Class_key != hm2._Class_key
and hm1._Marker_key = m._Marker_key
go
 
set nocount off
go

print ""
print "Duplicate Orthologies By Class"
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

select distinct r._Class_key, m._Organism_key, m.symbol
into #homology
from MRK_Homology_Cache r, MRK_Marker m
where r._Marker_key = m._Marker_key
go

select distinct _Class_key
into #duplicates
from #homology
group by _Class_key, _Organism_key having count(*) > 1
go

set nocount off
go

print ""
print "Duplicate Orthologies By Organism"
print ""

select distinct h.symbol, substring(h.commonName,1,25), h.jnum, h._Class_key 
from HMD_Homology_View h, #duplicates d
where d._Class_key = h._Class_key
order by h._Class_key, h.commonName
go

