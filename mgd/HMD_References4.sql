set nocount on
go

/* Select all references where Homology and Probes are selected */

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
and bd.dataSet = 'Molecular Segments'
and ba.isNeverUsed = 0)
go

select * 
into #noData
from #references c
where not exists (select r.* from HMD_Homology r where c._Refs_key = r._Refs_key)
go

set nocount off
go

print "" 
print "References selected for Orthology and Probes w/out Orthology Data, w/ Probe Data"
print "(excludes NEVER USED)"
print "" 
 
select distinct c.jnum, substring(c.title,1,150)
from #noData c, PRB_Reference r
where c._Refs_key = r._Refs_key
order by c.jnum 
go 
  
print "" 
print "References selected for Orthology and Probes w/out Orthology Data, w/out Probe Data"
print "(excludes NEVER USED)"
print "" 
 
select distinct c.jnum, substring(c.title,1,150)
from #noData c
where not exists (select r.* from PRB_Reference r where c._Refs_key = r._Refs_key)
order by c.jnum 
go 
  
