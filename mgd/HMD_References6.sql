set nocount on
go

/* Select all references where only Homology is selected and never used */

select c._Refs_key, c.jnum, c.title
into #references
from BIB_All_View c 
where c.dbs = 'Homology*/' or c.dbs = 'Homology*'
go

select * 
into #noData
from #references c
where not exists (select r.* from HMD_Homology r where c._Refs_key = r._Refs_key)
go

set nocount off
go

print "" 
print "References selected only for Homology but statused as NEVER USED - J# < 40000" 
print "" 
 
select c.jnum, substring(c.title,1,150)
from #noData c
where c.jnum < 40000
order by c.jnum 
go 
  
print "" 
print "References selected only for Homology but statused as NEVER USED - J# >= 40000" 
print "" 
 
select c.jnum, substring(c.title,1,150)
from #noData c
where c.jnum >= 40000
order by c.jnum 
go 

