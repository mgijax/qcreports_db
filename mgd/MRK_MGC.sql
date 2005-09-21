print ""
print "MGC Sequence Accession IDs in MGI which are also"
print "associated with a Nomen record with a status other"
print "than Deleted or Broadcast;"
print "that are ALSO associated with ONLY a sequence detail record in MGI"
print ""

select a.accID
from ACC_Accession a
where a._LogicalDB_key = 9
and a.prefixPart = "BC"
and a._MGIType_key = 19
and exists (select 1 from ACC_Accession na, NOM_Marker_View n
where a.accID = na.accID
and na._MGIType_key = 21
and na._Object_key = n._Nomen_key
and n.status not in ('Deleted', 'Broadcast - Official', 'Broadcast - Interim'))
and not exists (select 1 from SEQ_Marker_Cache c
where a._Object_key = c._Sequence_key and c._Organism_key = 1)
and not exists (select 1 from SEQ_Probe_Cache c
where a._Object_key = c._Sequence_key)
order by a.accID
go

print ""
print "MGC Sequence Accession IDs in MGD which are also"
print "associated with a Nomen record with a status other"
print "than Deleted or Broadcast;"
print "that are ALSO associated with with any other MGI record in"
print "ADDITION to the sequence detail record."
print ""

select a.accID
from ACC_Accession a
where a._LogicalDB_key = 9
and a.prefixPart = "BC"
and a._MGIType_key = 19
and exists (select 1 from ACC_Accession na, NOM_Marker_View n
where a.accID = na.accID
and na._MGIType_key = 21
and na._Object_key = n._Nomen_key
and n.status not in ('Deleted', 'Broadcast - Official', 'Broadcast - Interim'))
and exists (select 1 from SEQ_Marker_Cache c
where a._Object_key = c._Sequence_key and c._Organism_key = 1)
union
select a.accID
from ACC_Accession a
where a._LogicalDB_key = 9
and a.prefixPart = "BC"
and a._MGIType_key = 19
and exists (select 1 from ACC_Accession na, NOM_Marker_View n
where a.accID = na.accID
and na._MGIType_key = 21
and na._Object_key = n._Nomen_key
and n.status not in ('Deleted', 'Broadcast - Official', 'Broadcast - Interim'))
and exists (select 1 from SEQ_Probe_Cache c
where a._Object_key = c._Sequence_key)
order by a.accID
go

