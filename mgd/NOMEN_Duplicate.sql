set nocount on
go

select *
into #nomen
from NOM_Marker
where datepart(yy, broadcast_date) > 1999
group by symbol having count(*) > 1
go

set nocount off
go

print ""
print "Nomenclature Duplicate Symbols"
print ""

select v.symbol, v.chromosome, v.createdBy, v.broadcastBy, r.jnumID
from #nomen n, NOM_Marker_View v, MGI_Reference_Nomen_View r
where n._Nomen_key = v._Nomen_key
and v._Nomen_key = r._Object_key
and r.assocType = "Primary"
order by v.symbol, v.broadcastBy, v.createdBy
go
