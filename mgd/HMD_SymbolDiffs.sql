print ""
print "MGD Mouse Symbols which differ from Orthologous Human Symbols"
print ""

select distinct 
	m1.symbol "MGI Symbol", 
	m2.symbol "MGI Human Symbol", 
	a1.accID "MGI ID", 
	substring(m1.name, 1, 40) "MGI Name",
	l.locusID "LL ID",
	substring(m2.name, 1, 40) "Human Name"

from HMD_Homology r1, HMD_Homology_Marker h1,
     HMD_Homology r2, HMD_Homology_Marker h2,
     MRK_Marker m1, MRK_Marker m2, MRK_ACC_View a1, MRK_ACC_View a2,
     tempdb..LL l

where m1._Species_key = 1 
and m1._Marker_key = h1._Marker_key 
and h1._Homology_key = r1._Homology_key 
and r1._Class_key = r2._Class_key 
and r2._Homology_key = h2._Homology_key 
and h2._Marker_key = m2._Marker_key 
and m2._Species_key = 2 
and m1.symbol != m2.symbol
and m2.symbol not like '*%'
and m1._Marker_key = a1._Object_key
and a1.prefixPart = "MGI:"
and a1.preferred = 1
and m2._Marker_key = a2._Object_key
and a2.prefixPart = "GDB:"
and a2.accID = l.gsdbid
order by m1.symbol
go

