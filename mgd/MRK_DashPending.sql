set nocount on
go

select m._Marker_key, m.symbol, name = substring(m.name,1,50), m.creation_date
into #marker
from MRK_Marker m
where m.symbol like '%-pending'
and m._Marker_Status_key = 1
go

set nocount off
go

print ""
print "-pending Markers"
print ""

select distinct m.symbol "Mouse Symbol", m2.symbol "Human Symbol", m.name "Mouse Name", m.creation_date
from #marker m, HMD_Homology r1, HMD_Homology_Marker h1,
HMD_Homology r2, HMD_Homology_Marker h2, MRK_Marker m2
where m._Marker_key = h1._Marker_key
and h1._Homology_key = r1._Homology_key
and r1._Class_key = r2._Class_key
and r2._Homology_key = h2._Homology_key
and h2._Marker_key = m2._Marker_key
and m2._Species_key = 2
union
select distinct m.symbol, null, m.name, m.creation_date
from #marker m
where not exists (select 1 from HMD_Homology r1, HMD_Homology_Marker h1,
HMD_Homology r2, HMD_Homology_Marker h2, MRK_Marker m2
where m._Marker_key = h1._Marker_key
and h1._Homology_key = r1._Homology_key
and r1._Class_key = r2._Class_key
and r2._Homology_key = h2._Homology_key
and h2._Marker_key = m2._Marker_key
and m2._Species_key = 2)
order by m.creation_date, m.symbol
go

