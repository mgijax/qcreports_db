print ""
print "GXD Assays with Markers which are not Genes"
print ""

select v.mgiID, v.jnumID, v.symbol, t.name, v.assayType
from GXD_Assay_View v, MRK_Marker m, MRK_Types t
where v._Marker_key = m._Marker_key
and m._Marker_Type_key != 1
and m._Marker_Type_key = t._Marker_Type_key
order by v.symbol
go

print ""
print "GXD Index with Markers which are not Genes"
print ""

select v.jnumID, v.symbol, t.name
from GXD_Index_View v, MRK_Marker m, MRK_Types t
where v._Marker_key = m._Marker_key
and m._Marker_Type_key != 1
and m._Marker_Type_key = t._Marker_Type_key
order by v.symbol
go

