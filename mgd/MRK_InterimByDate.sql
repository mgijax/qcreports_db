set nocount on
go

/* select phenotypic mutants */
select distinct m._Marker_key
into #mutants
from MRK_Marker m, ALL_Allele a
where m._Marker_Type_key = 1
and m._Marker_key = a._Marker_key
and m.symbol = a.symbol
and not exists (select 1 from MRK_Acc_View a
where m._Marker_key = a._Object_key
and a._LogicalDB_key in (9,13,27,41))
go

/* select interim markers; exclude phenotypic mutants */
select m._Marker_key, m.symbol, name = substring(m.name,1,50), m.creation_date
into #marker
from MRK_Marker m
where m._Species_key = 1
and m._Marker_Status_key = 3
and not exists (select 1 from #mutants t where m._Marker_key = t._Marker_key)
go

select distinct msymbol = m.symbol, hsymbol = m2.symbol, m.name, m.creation_date
into #homology
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
go

select h.*, hstatus = "O"
into #results
from #homology h, tempdb..LL l
where h.hsymbol = l.osymbol
and l.taxID = 9606
union
select h.*, hstatus = "I"
from #homology h, tempdb..LL l
where h.hsymbol = l.isymbol
and l.taxID = 9606
union
select h.*, hstatus = "?"
from #homology h
where not exists (select 1 from tempdb..LL l
where l.taxID = 9606 and (h.hsymbol = l.osymbol or h.hsymbol = l.isymbol))
go

set nocount off
go

print ""
print "Interim Markers"
print "(sorted by human symbol status (if applicable) and date)"
print ""

select msymbol "Mouse Symbol", hstatus "Status", hsymbol "Human Symbol", name "Mouse Name", creation_date
from #results
order by hstatus desc, creation_date
go

