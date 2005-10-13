print ""
print "Markers of type pseudogene mapped to PIRSF superfamilies"
print ""

select mt.name, acc1.accid, m.symbol, acc2.accid, t.term
from mrk_marker m, mrk_types mt, acc_accession acc1, acc_accession acc2, voc_annot a, voc_term t
where a._annottype_key = 1007
and acc1._object_key = a._object_key
and acc1._mgitype_key = 2
and acc1._logicaldb_key = 1
and acc1.preferred = 1
and m._marker_key = a._object_key
and mt._marker_type_key = m._marker_type_key
and m._marker_type_key = 7
and acc2._object_key = a._term_key
and acc2._mgitype_key = 13
and t._term_key = a._term_key
go
