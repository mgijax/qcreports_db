set nocount on
go

select r._Refs_key
into #refs1
from BIB_Refs r
where r.year >= 1975
and datalength(r.abstract) = 0
go

select r._Refs_key, a.accID
into #refs2
from #refs1 r, ACC_Accession a
where r._Refs_key = a._Object_key
and a._MGIType_key = 1
and a.LogicalDB = 'Medline'
go

select r.*
into #refs3
from #refs2 r
where not exists
(select n.* from BIB_Notes n
where r._Refs_key = n._Refs_key and n.note like '%No Abstract Available%')
go

set nocount off
go

print ""
print "References w/ Medline UI and No Abstract"
print ""

select distinct r.accID, c.jnum, substring(c.short_citation, 1, 50)
from #refs3 r, BIB_All_View c
where r._Refs_key = c._Refs_key
order by c.year, c._primary
go
 
