print ""
print "MGC Sequence Accession IDs in MGD which are also"
print "associated with a Nomen record with a status other"
print "than Deleted or Broadcast"
print ""

select a.accID
from ACC_Accession a
where a._LogicalDB_key = 9
and a.prefixPart = "BC"
and exists (select 1 from nomen..ACC_Accession na, nomen..MRK_Nomen n
where a.accID = na.accID
and na._Object_key = n._Nomen_key
and n._Marker_Status_key not in (2,5))
order by a.accID
go

