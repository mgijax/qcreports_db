set nocount on
go

select distinct mouseMarker = m._Marker_key, mouseChr = m.chromosome, 
       humanMarker = m2._Marker_key, humanChr = m2.chromosome
into #all
from MRK_Marker m, HMD_Homology h1, HMD_Homology_Marker hm1, HMD_Homology h2, HMD_Homology_Marker hm2, MRK_Marker m2
where m._Organism_key = 1
and hm1._Marker_key = m._Marker_key
and hm1._Homology_key = h1._Homology_key
and h1._Class_key = h2._Class_key
and h2._Homology_key = hm2._Homology_key
and hm2._Marker_key = m2._Marker_key
and m2._Organism_key = 2
go

select * 
into #singles
from #all
group by mouseChr, humanChr having count(*) = 1
go

select s.mouseMarker, s.humanMarker, a.accID
into #homologies
from #singles s, HMD_Homology h1, HMD_Homology_Marker hm1, HMD_Homology h2, HMD_Homology_Marker hm2, ACC_Accession a
where s.mouseMarker = hm1._Marker_key
and hm1._Homology_key = h1._Homology_key
and h1._Class_key = h2._Class_key
and h2._Homology_key = hm2._Homology_key
and hm2._Marker_key = s.humanMarker
and h1._Refs_key = a._Object_key
and a._MGIType_key = 1
and a._LogicalDB_key = 1
and a.prefixPart = "J:"
go

set nocount off
go

print ""
print "Mouse/Human Singletons"
print ""

select m1.symbol "Mouse Symbol", substring(ms.status,1,10) "Status", m1.chromosome, m1.cytogeneticOffset, o.offset,
m2.symbol "Human Symbol", m2.chromosome, m2.cytogeneticOffset, h.accID
from #singles s, #homologies h, MRK_Marker m1, MRK_Marker m2, MRK_Status ms, MRK_Offset o
where s.mouseMarker = h.mouseMarker
and s.humanMarker = h.humanMarker
and s.mouseMarker = m1._Marker_key
and m1._Marker_Status_key = ms._Marker_Status_key
and m1._Marker_key = o._Marker_key
and o.source = 0
and s.humanMarker = m2._Marker_key
order by m1.symbol
go

