print ""
print "MGC Sequence Accession IDs in MGD which are also"
print "associated with a Nomen record with a status other"
print "than Deleted or Broadcast"
print ""

select a.accID
from ACC_Accession a
where a._LogicalDB_key = 9
and a.prefixPart = "BC"
and a._MGIType_key != 21
and exists (select 1 from ACC_Accession na, NOM_Marker_View n
where a.accID = na.accID
and na._MGIType_key = 21
and na._Object_key = n._Nomen_key
and n.status not in ('Deleted', 'Broadcast - Official', 'Broadcast - Interim'))
order by a.accID
go

