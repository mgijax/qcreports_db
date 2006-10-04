set nocount on
go

/* Select all references where Homology is selected */

select r._Refs_key
into #references
from BIB_Refs r
where exists (select 1 from BIB_DataSet_Assoc ba, BIB_DataSet bd
where r._Refs_key = ba._Refs_key
and ba._DataSet_key = bd._DataSet_key
and bd.dataSet = 'Homology'
and ba.isNeverUsed = 0)
order by r._Refs_key
go

create unique clustered index index_Refs_key on #references(_Refs_key) with sorted_data
go

/* Select all references not used in Homology but x-referenced to a marker */

select distinct r._Refs_key
into #nodata
from #references r, MRK_Reference m
where r._Refs_key = m._Refs_key
and not exists (select h.* from MRK_Homology_Cache h where m._Marker_key = h._Marker_key)
and not exists (select h.* from MRK_Homology_Cache h where m._Refs_key = h._Refs_key)
go

set nocount off
go

print "" 
print "References selected for Orthology w/ no Orthology Data"
print "With at least one reference-to-gene Association"
print "(excludes NEVER USED References)"
print "" 
 
select b.jnum
from #nodata n, BIB_All_View b
where n._Refs_key = b._Refs_key
order by jnum desc
go 

