set nocount on
go

/* select phenotypic mutants */
select distinct m._Marker_key
into #mutants
from MRK_Marker m, ALL_Allele a
where m._Marker_Type_key = 1
and m._Marker_key = a._Marker_key
and m.symbol = a.symbol
and not exists (select 1 from ACC_Accession a
where m._Marker_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_key in (9,13,27,41))
go

create index idx1 on #mutants(_Marker_key)
go

/* select interim markers; exclude phenotypic mutants */
select m._Marker_key, m.symbol, name = substring(m.name,1,50), m.creation_date, h.jnum
into #marker
from MRK_Marker m, MRK_History_Ref_View h
where m._Organism_key = 1
and m._Marker_Status_key = 3
and m._Marker_key = h._Marker_key
and m._Marker_key = h._History_key
and h._Marker_Event_key = 1
and not exists (select 1 from #mutants t where m._Marker_key = t._Marker_key)
go

create index idx1 on #markers(_Marker_key)
go

select distinct msymbol = m.symbol, hsymbol = m2.symbol, m.name, m.creation_date, m.jnum
into #homology
from #marker m, HMD_Homology r1, HMD_Homology_Marker h1,
HMD_Homology r2, HMD_Homology_Marker h2, MRK_Marker m2
where m._Marker_key = h1._Marker_key
and h1._Homology_key = r1._Homology_key
and r1._Class_key = r2._Class_key
and r2._Homology_key = h2._Homology_key
and h2._Marker_key = m2._Marker_key
and m2._Organism_key = 2
union
select distinct m.symbol, null, m.name, m.creation_date, m.jnum
from #marker m
where not exists (select 1 from HMD_Homology r1, HMD_Homology_Marker h1,
HMD_Homology r2, HMD_Homology_Marker h2, MRK_Marker m2
where m._Marker_key = h1._Marker_key
and h1._Homology_key = r1._Homology_key
and r1._Class_key = r2._Class_key
and r2._Homology_key = h2._Homology_key
and h2._Marker_key = m2._Marker_key
and m2._Organism_key = 2)
go

create index idx1 on #homology(hsymbol)
go

select h.*, hstatus = "O"
into #results
from #homology h, radar..DP_EntrezGene_Info e
where h.hsymbol = e.symbol and e.taxID = 9606
union
select h.*, hstatus = "?"
from #homology h
where not exists (select 1 from radar..DP_EntrezGene_Info e
where h.hsymbol = e.symbol and e.taxID = 9606)
go

create index idx1 on #results(hstatus)
go

set nocount off
go

print ""
print "Interim Markers"
print "(sorted by human symbol status (if applicable) and jnum)"
print ""

select msymbol "Mouse Symbol", hstatus "Status", hsymbol "Human Symbol", name "Mouse Name", jnum, creation_date
from #results
order by hstatus desc, jnum
go

