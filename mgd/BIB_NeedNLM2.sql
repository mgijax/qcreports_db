print ""
print "References Which Need NLM Updates"
print "in Medline query format:"
print ""
print "first author [AU] AND year [YR] AND journal name [TA] AND first page [PG]"
print ""

select r._primary + " [AU] AND "  
+ convert(char(4), r.year) + " [YR] AND " + 
r.journal + " [TA] " + 
substring(r.pgs, 1, charindex("-", r.pgs) - 1)  + " [PG]"
from BIB_Refs r
where r.NLMstatus = 'Y'
and r.pgs like "%-%"
and not exists
(select a._Accession_key from BIB_Acc_View a
where a._Object_key = r._Refs_key
and a._LogicalDB_key in (7,29))
union
select r._primary + " [AU] AND "  
+ convert(char(4), r.year) + " [YR] AND " + 
r.journal + " [TA] " + 
r.pgs + " [PG]"
from BIB_Refs r
where r.NLMstatus = 'Y'
and r.pgs not like "%-%"
and not exists
(select a._Accession_key from BIB_Acc_View a
where a._Object_key = r._Refs_key
and a._LogicalDB_key in (7,29))
order by r.year, r._primary
go

