print ""
print "Mouse Markers with no Sequence ID but with Human Homology"
print "(Excludes DNA Segments)"
print ""

select distinct m.symbol "Symbol"
from MRK_Marker m
where m._Species_key = 1
and m._Marker_Type_key != 2
and exists (select 1 
from HMD_Homology h1, HMD_Homology_Marker hm1, HMD_Homology h2, HMD_Homology_Marker hm2,
MRK_Marker m2
where hm1._Marker_key = m._Marker_key
and hm1._Homology_key = h1._Homology_key
and h1._Class_key = h2._Class_key
and h2._Homology_key = hm2._Homology_key
and hm2._Marker_key = m2._Marker_key
and m2._Species_key = 2)
and not exists (select 1 from MRK_ACC_View a
where m._Marker_key = a._Object_key
and a._LogicalDB_Key = 9)
order by m.symbol
go

