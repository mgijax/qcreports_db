set nocount on
go

/* Select all references where Homology is selected */

select r._Refs_key
into #references
from BIB_Refs r
where r.dbs like '%Homology%' 
and r.dbs not like '%Homology*%'
order by r._Refs_key
go

create unique clustered index index_Refs_key on #references(_Refs_key) with sorted_data
go

/* Select all references not used in Homology but x-referenced to a marker */

select distinct r._Refs_key
into #nodata
from #references r, MRK_Reference m
where not exists (select h.* from HMD_Homology h where r._Refs_key = h._Refs_key)
and r._Refs_key = m._Refs_key
go

set nocount off
go

print "" 
print "References selected for Homology w/ no Homology Data"
print "With at least one reference-to-gene Association"
print "(excludes NEVER USED References)"
print "" 
 
select b.jnum
from #nodata n, BIB_All_View b
where n._Refs_key = b._Refs_key
order by jnum 
go 

