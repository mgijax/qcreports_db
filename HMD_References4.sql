set nocount on
go

/* Select all references where Homology and Probes are selected */

select c._Refs_key, c.jnum, c.title
into #references
from BIB_All_View c 
where c.dbs like '%Homology%' 
and c.dbs like '%Probes%'
and c.dbs not like '%Homology*%'
and c.dbs not like '%Probes*%'
go

select * 
into #noData
from #references c
where not exists (select r.* from HMD_Homology r where c._Refs_key = r._Refs_key)
go

set nocount off
go

print "" 
print "References selected for Homology and Probes w/out Homology Data, w/ Probe Data"
print "(excludes NEVER USED)"
print "" 
 
select distinct c.jnum, substring(c.title,1,150)
from #noData c, PRB_Reference r
where c._Refs_key = r._Refs_key
order by c.jnum 
go 
  
print "" 
print "References selected for Homology and Probes w/out Homology Data, w/out Probe Data"
print "(excludes NEVER USED)"
print "" 
 
select distinct c.jnum, substring(c.title,1,150)
from #noData c
where not exists (select r.* from PRB_Reference r where c._Refs_key = r._Refs_key)
order by c.jnum 
go 
  
