
print ""
print "Full Coded References that are missing a Gene in the Index"
print ""
print "excluded:"
print "  Freeman reference (J:46439)"
print "  Deltagen reference (J:101679)"
print ""

select distinct b.accID, m.symbol
from GXD_Assay a, MRK_Marker m, ACC_Accession b
where a._Refs_key not in (46734, 102744)
and not exists (select 1 from GXD_Index i
where a._Refs_key = i._Refs_key
and a._Marker_key = i._Marker_key)
and a._Marker_key = m._Marker_key
and a._Refs_key = b._Object_key
and b._MGIType_key = 1
and b._LogicalDB_key = 1
and b.prefixPart = "J:"
order by b.numericPart
go

