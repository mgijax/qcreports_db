print ""
print "Mouse/Human Singletons"
print ""

select distinct m.symbol "Mouse Symbol", m.chromosome, m.cytogeneticOffset, o.offset,
m2.symbol "Human Symbol", m2.chromosome, m2.cytogeneticOffset, a.accID
from MRK_Marker m, MRK_Offset o,
HMD_Homology h1, HMD_Homology_Marker hm1, HMD_Homology h2, HMD_Homology_Marker hm2, MRK_Marker m2,
ACC_Accession a
where m._Species_key = 1
and m._Marker_key = o._Marker_key
and o.source = 0
and hm1._Marker_key = m._Marker_key
and hm1._Homology_key = h1._Homology_key
and h1._Class_key = h2._Class_key
and h2._Homology_key = hm2._Homology_key
and hm2._Marker_key = m2._Marker_key
and m2._Species_key = 2
and h1._Refs_key = a._Object_key
and a._MGIType_key = 1
and a._LogicalDB_key = 1
and a.prefixPart = "J:"
and not exists (select 1 
from HMD_Homology h1, HMD_Homology_Marker hm1, HMD_Homology h2, HMD_Homology_Marker hm2, MRK_Marker m2
where hm1._Marker_key = m._Marker_key
and hm1._Homology_key = h1._Homology_key
and h1._Class_key = h2._Class_key
and h2._Homology_key = hm2._Homology_key
and hm2._Marker_key = m2._Marker_key
and m2._Species_key not in (1,2))
order by m.symbol
go

