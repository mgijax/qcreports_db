print ""
print "Mouse Genes that have Rat Homologs but no GO associations"
print ""

select distinct a.accID, m1.symbol, name = substring(m1.name, 1, 100)
from MRK_Acc_View a, MRK_Marker m1, HMD_Homology_Marker hm1, HMD_Homology h1,
HMD_Homology_Marker hm2, HMD_Homology h2, MRK_marker m2
where m1._Species_key = 1
and m1._Marker_Type_key = 1
and m1._Marker_key = hm1._Marker_key
and hm1._Homology_key = h1._Homology_key
and h1._Class_key = h2._Class_key
and h2._Homology_key = hm2._Homology_key
and hm2._Marker_key = m2._Marker_key
and m2._Species_key = 40
and not exists (select 1 from GO_MarkerGO g
where m1._Marker_key = g._Marker_key)
and m1._Marker_key = a._Object_key
and a.prefixPart = "MGI:"
and a.preferred = 1
order by m1.symbol
go
