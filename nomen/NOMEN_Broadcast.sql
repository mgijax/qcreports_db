print ""
print "Nomenclature Symbols Broadcast Within Last 3 Days"
print ""

select n.symbol, n.chromosome, n.submittedBy, n.broadcastBy, r.jnumID
from MRK_Nomen_View n, MRK_Nomen_Reference_View r
where n.broadcast_date between dateadd(day, -3, getdate()) and dateadd(day, -0, getdate())
and n._Nomen_key = r._Nomen_key
and r.isPrimary = 1
order by n.broadcast_date, n.broadcastBy, n.submittedBy
go
