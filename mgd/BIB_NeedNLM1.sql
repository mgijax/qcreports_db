set nocount on
go

select _Refs_key
into #nlm
from BIB_Refs r
where NLMstatus = 'Y'
and not exists
(select a._Accession_key from ACC_Accession a
where a._MGIType_key = 1
and a._Object_key = r._Refs_key
and a._LogicalDB_key in (7,29))
go

set nocount off
go

print ""
print "References Which Need NLM Updates"
print ""

select b.jnumID, substring(b.short_citation, 1, 75)
from BIB_All_View b, #nlm n
where n._Refs_key = b._Refs_key
order by year, _primary
go

