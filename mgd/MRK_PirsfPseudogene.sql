print ""
print "Markers of Type 'Pseudogene' mapped to PIRSF superfamilies"
print ""

select acc1.accID, symbol = substring(m.symbol,1,25), acc2.accID, term = substring(t.term,1,50)
from MRK_Marker m, ACC_Accession acc1, ACC_Accession acc2, VOC_Annot a, VOC_Term t
where a._AnnotType_key = 1007
and acc1._Object_key = a._Object_key
and acc1._MGIType_key = 2
and acc1._LogicalDB_key = 1
and acc1.preferred = 1
and m._Marker_key = a._Object_key
and m._Marker_Type_key = 7
and acc2._Object_key = a._Term_key
and acc2._MGIType_key = 13
and t._Term_key = a._Term_key
go
