set nocount on
go

/* Select all references where Homology and MLC are the only datasets selected */

select c._Refs_key, c.jnum, c.title
into #references
from BIB_All_View c
where exists (select 1 from BIB_DataSet_Assoc ba, BIB_DataSet bd
where c._Refs_key = ba._Refs_key
and ba._DataSet_key = bd._DataSet_key
and bd.dataSet = 'Homology'
and ba.isNeverUsed = 0)
and exists (select 1 from BIB_DataSet_Assoc ba, BIB_DataSet bd
where c._Refs_key = ba._Refs_key
and ba._DataSet_key = bd._DataSet_key
and bd.dataSet = 'Mouse Locus Catalog'
and ba.isNeverUsed = 0)
and not exists (select 1 from BIB_DataSet_Assoc ba, BIB_DataSet bd
where c._Refs_key = ba._Refs_key
and ba._DataSet_key = bd._DataSet_key
and bd.dataSet not in ('Homology', 'Mouse Locus Catalog'))
go

select * 
into #noData
from #references c
where not exists (select r.* from HMD_Homology r where c._Refs_key = r._Refs_key)
go

set nocount off
go

print "" 
print "References selected for Orthology and MLC only w/out Orthology Data - J# < 40000" 
print "(excludes NEVER USED)"
print "" 
 
select c.jnum, substring(c.title,1,150)
from #noData c
where c.jnum < 40000
order by c.jnum 
go 
  
print "" 
print "References selected for Orthology and MLC only w/out Orthology Data - #J >= 40000" 
print "(excludes NEVER USED)"
print "" 
 
select c.jnum, substring(c.title,1,150)
from #noData c
where c.jnum >= 40000
order by c.jnum 
go 


