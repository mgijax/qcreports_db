print ""
print "Nomenclature In Progress Symbols"
print ""

select n.symbol, n.chromosome, u.login, r.jnumID
from NOM_Marker n, VOC_Term t, MGI_User u, MGI_Reference_Nomen_View r
where n._NomenStatus_key = t._Term_key
and t.term = "In Progress"
and n._CreatedBy_key = u._User_key
and n._Nomen_key = r._Object_key
and r.assocType = "Primary"
order by u.login, n.symbol
go
