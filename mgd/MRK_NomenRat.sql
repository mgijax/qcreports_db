set nocount on
go

select distinct r._Marker_key, r._Current_key, r.symbol, r.current_symbol
into #markers
from MRK_History h, MRK_Current_View r, HMD_Homology_Marker hm
where h._Marker_Event_key in (2,3,4,5)
and h._History_key = r._Marker_key
and r._Current_key = hm._Marker_key
go

set nocount off
go

print ""
print "Mouse Symbols with nomenclature changes which contain Rat homologs with unofficial nomenclature"
print ""

select distinct m.current_symbol "New Mouse Symbol", m2.symbol "Rat Symbol"
from #markers m, 
HMD_Homology_Marker hm1, HMD_Homology h1, HMD_Homology h2, HMD_Homology_Marker hm2, MRK_Marker m2
where m._Current_key = hm1._Marker_key
and hm1._Homology_key = h1._Homology_key
and h1._Class_key = h2._Class_key
and h2._Homology_key = hm2._Homology_key
and hm2._Marker_key = m2._Marker_key
and m2._Species_key = 40
and m2.symbol like '*%'
and m2.symbol != "*" + m.current_symbol + "*"
order by m.current_symbol
go

