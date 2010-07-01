
print ""
print "Gm Markers without Gene Model Associations"
print ""
print "   where name begins 'predicted gene'"
print "   and status = 'official' or 'interim'"
print ""

select distinct m.symbol, a.accID, substring(h.name,1,50) "old name"
from MRK_Marker m, ACC_Accession a, MRK_History h
where m._Organism_key = 1
and m._Marker_Status_key in (1,3)
and m.name like 'predicted gene%'
and not exists (select 1 from SEQ_Marker_Cache c
where m._Marker_key = c._Marker_key
and c._LogicalDB_key in (59,60,85))
and m._Marker_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_Key = 1
and a.prefixPart = "MGI:"
and a.preferred = 1
and m._Marker_key = h._Marker_key
and m.name != h.name
order by m.symbol
go

