set nocount on
go

select _Nomen_key
into #nomen
from MRK_Nomen
where broadcast_date between dateadd(day, -3, getdate()) and dateadd(day, -0, getdate())
go

set nocount off
go

print ""
print "Nomenclature Symbols Broadcast Within Last 3 Days"
print ""

select v.symbol, v.chromosome, v.submittedBy, v.broadcastBy, r.jnumID
from #nomen n, MRK_Nomen_View v, MRK_Nomen_Reference_View r
where n._Nomen_key = v._Nomen_key
and v._Nomen_key = r._Nomen_key
and r.isPrimary = 1
order by v.broadcast_date, v.broadcastBy, v.submittedBy
go
