print ""
print "Mouse Genes with Sequence ID but no Human Homology"
print "(Excludes RIKEN genes, Expressed Sequence, EST, Hypothetical)"
print ""

select distinct m.symbol "Symbol", a.accID "Seq ID"
from MRK_Marker m, MRK_ACC_View a
where m._Species_key = 1
and m._Marker_Type_key = 1
and m.symbol not like "%Rik"
and m.name not like "%expressed%"
and m.name not like "EST%"
and m.name not like "%hypothetical%"
and m._Marker_key = a._Object_key
and a._LogicalDB_Key = 9
and not exists (select 1 
from HMD_Homology h1, HMD_Homology_Marker hm1, HMD_Homology h2, HMD_Homology_Marker hm2,
MRK_Marker m2
where hm1._Marker_key = m._Marker_key
and hm1._Homology_key = h1._Homology_key
and h1._Class_key = h2._Class_key
and h2._Homology_key = hm2._Homology_key
and hm2._Marker_key = m2._Marker_key
and m2._Species_key = 2)
order by m.symbol
go

