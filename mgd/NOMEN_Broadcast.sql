set nocount on
go

select _Nomen_key
into #nomen
from NOM_Marker
where broadcast_date between dateadd(day, -3, getdate()) and dateadd(day, -0, getdate())
go

set nocount off
go

print ""
print "Nomenclature Symbols Broadcast Within Last 3 Days"
print ""

select v.symbol, substring(v.name, 1, 50) "name", substring(v.status,1,25) "status", 
v.chromosome, v.createdBy, v.broadcastBy, r.jnumID, convert(char(10), v.broadcast_date, 101) "broadcast date"
from #nomen n, NOM_Marker_View v, MGI_Reference_Nomen_View r
where n._Nomen_key = v._Nomen_key
and v._Nomen_key = r._Object_key
and r.assocType = "Primary"
order by v.broadcastBy, v.broadcast_date, v.createdBy
go
