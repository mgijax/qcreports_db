set nocount on
go

select distinct 
       m_Marker_key = m1._Marker_key, msymbol = substring(m1.symbol,1,30), mname = substring(m1.name, 1, 40), 
       mstatus = substring(upper(ms.status), 1, 1),
       h_Marker_key = m2._Marker_key, hsymbol = substring(m2.symbol,1,30), hname = substring(m2.name, 1, 40),
       m2.modification_date
into #homology
from HMD_Homology r1, HMD_Homology_Marker h1,
     HMD_Homology r2, HMD_Homology_Marker h2,
     MRK_Marker m1, MRK_Marker m2, MRK_Status ms
where m1._Organism_key = 1 
and m1._Marker_Status_key = ms._Marker_Status_key
and m1._Marker_key = h1._Marker_key 
and h1._Homology_key = r1._Homology_key 
and r1._Class_key = r2._Class_key 
and r2._Homology_key = h2._Homology_key 
and h2._Marker_key = m2._Marker_key 
and m2._Organism_key = 2 
and m1.symbol != m2.symbol
and m1.symbol not like '%Rik'
go

create index idx1 on #homology(m_Marker_key)
go
create index idx2 on #homology(h_Marker_key)
go

select h.*, geneID = a.accID
into #markerswithids
from #homology h, MRK_ACC_View a
where h.h_Marker_key = a._Object_key
and a._LogicalDB_key = 55
union
select h.*, geneID = null
from #homology h
where not exists (select 1 from MRK_ACC_View a
where h.h_Marker_key = a._Object_key
and a._LogicalDB_key = 55)
go

create index idx1 on #markerswithids(m_Marker_key)
go

select m.*, synonym = substring(o.name, 1, 50)
into #markers
from #markerswithids m, MRK_Other o
where m.m_Marker_key *= o._Marker_key
and o.name not like "%Rik"
and o.name not like "MGC:%"
go

create index idx1 on #markers(geneID)
go
create index idx2 on #markers(hsymbol)
go

select m.*, hstatus = "O"
into #results
from #markers m, radar..DP_EntrezGene_Info e
where m.geneID = e.geneID and m.hsymbol = e.symbol
union
select m.*, hstatus = "?"
from #markers m
where not exists (select 1 from radar..DP_EntrezGene_Info e
where m.geneID = e.geneID and m.hsymbol = e.symbol)
go

create index idx1 on #results(hstatus)
go

set nocount off
go

print ""
print "MGI Mouse Symbols which differ from Orthologous Human Symbols"
print "Excludes RIKEN symbols"
print "(sorted by human status, mouse status, mouse symbol)"
print ""

select msymbol "MGI Symbol", 
       mstatus "MGI Status",
       hsymbol "MGI Human Symbol", 
       hstatus "Human Status",
       synonym "MGI Synonym"
from #results
order by hstatus desc, mstatus desc, msymbol
go

