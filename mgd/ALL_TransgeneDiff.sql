
print ""
print "Approved Transgenes where :"
print "    the marker name and the allele name are not identical"
print "    or"
print "    the marker symbol and the allele symbol are not identical"
print ""

select m.symbol "Marker Symbol", substring(m.name,1,60) "Marker Name", 
       a.symbol "Allele Symbol", substring(a.name,1,60) "Allele Name"
from ALL_Allele a, ALL_Marker_Assoc am, MRK_Marker m
where a._Allele_Status_key = 847114
and a._Allele_key = am._Allele_key
and am._Marker_key = m._Marker_key
and m._Marker_Type_key = 12
and (a.symbol != m.symbol or a.name != m.name)
order by m.symbol
go

