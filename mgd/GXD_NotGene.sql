print ""
print "GXD Assays with Markers which are not Genes"
print ""

select v.mgiID, v.jnumID, v.symbol, v.assayType
from GXD_Assay_View v, MRK_Marker m
where v._Marker_key = m._Marker_key
and m._Marker_Type_key != 1
order by v.symbol
go

