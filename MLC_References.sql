set nocount on
go

/* References that are only associated with MLC records */

select distinct r._Refs_key
into #references
from MLC_Reference r
where not exists (select r2.* from MRK_Reference r2
where r._Refs_key = r2._Refs_key)
go

set nocount off
go

print ""
print "References which only appear in MLC"
print ""

select b.jnum, substring(b.short_citation, 1, 75)
from #references r, BIB_All_View b
where r._Refs_key = b._Refs_key
order by b.year, b._primary
go

