set nocount on
go

select distinct 
       m_Marker_key = m1._Marker_key, msymbol = m1.symbol, mname = substring(m1.name, 1, 40), 
       h_Marker_key = m2._Marker_key, hsymbol = m2.symbol, hname = substring(m2.name, 1, 40)
into #homology
from HMD_Homology r1, HMD_Homology_Marker h1,
     HMD_Homology r2, HMD_Homology_Marker h2,
     MRK_Marker m1, MRK_Marker m2
where m1._Species_key = 1 
and m1._Marker_key = h1._Marker_key 
and h1._Homology_key = r1._Homology_key 
and r1._Class_key = r2._Class_key 
and r2._Homology_key = h2._Homology_key 
and h2._Marker_key = m2._Marker_key 
and m2._Species_key = 2 
and m1.symbol != m2.symbol
go

select h.*, mgiID = a1.accID, locusID = a2.accID
into #markers
from #homology h, MRK_ACC_View a1, MRK_ACC_View a2
where h.m_Marker_key = a1._Object_key
and a1.prefixPart = "MGI:"
and a1._LogicalDB_key = 1
and a1.preferred = 1
and h.h_Marker_key = a2._Object_key
and a2._LogicalDB_key = 24
union
select h.*, mgiID = a1.accID, locusID = null
from #homology h, MRK_ACC_View a1
where h.m_Marker_key = a1._Object_key
and a1.prefixPart = "MGI:"
and a1._LogicalDB_key = 1
and a1.preferred = 1
and not exists (select 1 from MRK_ACC_View a2
where h.h_Marker_key = a2._Object_key
and a2._LogicalDB_key = 24)
go

select m.*, type = "O"
into #results
from #markers m, tempdb..LL l
where m.locusID = l.locusID
and m.hsymbol = l.osymbol
union
select m.*, type = "I"
from #markers m, tempdb..LL l
where m.locusID = l.locusID
and m.hsymbol = l.isymbol
union
select m.*, type = "?"
from #markers m
where not exists (select 1 from tempdb..LL l
where m.locusID = l.locusID and (m.hsymbol = l.osymbol or m.hsymbol = l.isymbol))
go

set nocount off
go

print ""
print "MGD Mouse Symbols which differ from Orthologous Human Symbols"
print ""

select msymbol "MGI Symbol", 
       hsymbol "MGI Human Symbol", 
       type "Type",
       mgiID "MGI ID", 
       mname "MGI Name",
       locusID "LL ID",
       hname "Human Name"
from #results
order by type desc, msymbol
go

