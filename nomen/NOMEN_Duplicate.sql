set nocount on
go

select *
into #nomen
from MRK_Nomen
where datepart(yy, broadcast_date) > 1999
group by symbol having count(*) > 1
go

set nocount off
go

print ""
print "Nomenclature Duplicate Symbols"
print ""

select v.symbol, v.chromosome, v.submittedBy, v.broadcastBy, r.jnumID
from #nomen n, MRK_Nomen_View v, MRK_Nomen_Reference_View r
where n._Nomen_key = v._Nomen_key
and v._Nomen_key = r._Nomen_key
and r.isPrimary = 1
order by v.broadcast_date, v.broadcastBy, v.submittedBy
go
