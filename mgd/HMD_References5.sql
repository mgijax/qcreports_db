set nocount on
go

/* Select all references where Homology is selected */

select c._Refs_key, c.jnum, c.title
into #ref1
from BIB_All_View c
where c.dbs like '%Homology%' 
order by c._Refs_key
go

create unique clustered index index_Refs_key on #ref1(_Refs_key) with sorted_data
go

select r.*, mr._Marker_key, m.symbol
into #ref2
from #ref1 r, MRK_Reference mr (index index_Refs_key), MRK_Marker m
where r._Refs_key = mr._Refs_key
and mr._Marker_key = m._Marker_key
go

create nonclustered index index_Refs_key on #ref2(_Refs_key)
go

/* Select those references which are associated with only one gene */

select *
into #onegene
from #ref2
group by _Refs_key having count(*) = 1
go

set nocount off
go

print "" 
print "References selected for Homology w/ 1 Gene w/out Homology Data"
print "(excludes NEVER USED References)"
print "" 
 
select o.jnum, o.symbol
from #onegene o
where not exists (select 1 from HMD_Homology_Marker h where o._Marker_key = h._Marker_key)
order by o.jnum 
go 
  
print "" 
print "References selected for Homology w/ 1 Gene w/ Homology Data but No Human"
print "(excludes NEVER USED References)"
print "" 
 
select distinct o.jnum, o.symbol
from #onegene o, HMD_Homology_Marker hm1
where o._Marker_key = hm1._Marker_key
and not exists (select 1 from HMD_Homology h1, HMD_Homology_Marker hm1, 
	HMD_Homology h2, HMD_Homology_Marker hm2, MRK_Marker m2
	where hm1._Homology_key = h1._Homology_key
	and h1._Class_key = h2._Class_key
	and h2._Homology_key = hm2._Homology_key
	and hm2._Marker_key = m2._Marker_key
	and m2._Species_key = 1)
order by o.jnum 
go 
