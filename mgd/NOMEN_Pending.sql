print ""
print "Nomenclature In Progress Symbols"
print ""

select n.symbol, n.chromosome, n.createdBy, r.jnumID
from NOM_Marker_View n, MGI_Reference_Nomen_View r
where n.status = "In Progress"
and n._Nomen_key = r._Object_key
and r.assocType = "Primary"
order by n.createdBy, n.symbol
go
