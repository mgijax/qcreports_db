
set nocount on
go

select r._Refs_key, r._primary, r.year, r.pgs,
outputLine1 = r._primary + " [AU] AND "  
+ convert(char(4), r.year) + " [YR] AND " + 
r.journal + " [TA] AND "
into #refs
from BIB_Refs r
where r.NLMstatus = 'Y'
and not exists
(select a._Accession_key from BIB_Acc_View a
where a._Object_key = r._Refs_key
and a._LogicalDB_key in (7,29))
go

select r._Refs_key, r.year, r._primary, finalOutputLine = outputLine1 + " " + substring(r.pgs, 1, charindex("-", r.pgs) - 1)  + " [PG]"
into #orderedrefs
from #refs r
where r.pgs like "%-%"
union
select r._Refs_key, r.year, r._primary, finalOutputLine = outputLine1 + " " + r.pgs + " [PG]"
from #refs r
where r.pgs not like "%-%"
union
select r._Refs_key, r.year, r._primary, finalOutputLine = outputLine1
from #refs r
where r.pgs is null
order by r.year, r._primary
go

set nocount off
go

print ""
print "References Which Need NLM Updates"
print "in Medline query format:"
print ""
print "first author [AU] AND year [YR] AND journal name [TA] AND first page [PG]"
print ""

select finalOutputLine "Medline Format" from #orderedrefs
go

