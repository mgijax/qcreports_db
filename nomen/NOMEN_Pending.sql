print ""
print "Nomenclature In Progress Symbols"
print ""

select n.symbol, n.chromosome, n.submittedBy, r.jnumID
from MRK_Nomen_View n, MRK_Nomen_Reference_View r
where n._Marker_Status_key = 1
and n._Nomen_key = r._Nomen_key
and r.isPrimary = 1
order by n.submittedBy, n.symbol
go
