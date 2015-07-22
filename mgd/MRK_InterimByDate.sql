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

create index mutants_idx1 on #mutants(_Marker_key)
go

/* select interim markers; exclude phenotypic mutants */
select m._Marker_key, m.symbol, substring(m.name,1,50) as name, m.creation_date
into #marker
from MRK_Marker m
where m._Organism_key = 1
and m._Marker_Status_key = 3
and not exists (select 1 from #mutants t where m._Marker_key = t._Marker_key)
go

create index marker_idx1 on #marker(_Marker_key)
go

select distinct m.symbol as msymbol, m2.symbol as hsymbol, m.name, m.creation_date
into #homology
from #marker m, MRK_Cluster mc, MRK_ClusterMember h1, MRK_ClusterMember h2, MRK_Marker m2
where mc._ClusterSource_key = 9272151
and mc._Cluster_key = h1._Cluster_key
and h1._Marker_key = m._Marker_key
and h1._Cluster_key = h2._Cluster_key 
and h2._Marker_key = m2._Marker_key
and m2._Organism_key = 2
union
select distinct m.symbol as msymbol, null as hsymbol, m.name, m.creation_date
from #marker m
where not exists (select 1 from MRK_Cluster mc, MRK_ClusterMember h1, MRK_ClusterMember h2, MRK_Marker m2
where mc._ClusterSource_key = 9272151
and mc._Cluster_key = h1._Cluster_key
and h1._Marker_key = m._Marker_key
and h1._Cluster_key = h2._Cluster_key 
and h2._Marker_key = m2._Marker_key
and m2._Organism_key = 2
)
go

create index homology_idx1 on #homology(hsymbol)
go

select h.*, e.status as hstatus
into #results
from #homology h, radar.DP_EntrezGene_Info e
where h.hsymbol = e.symbol and e.taxID = 9606
union
select h.*, '?' as hstatus
from #homology h
where not exists (select 1 from radar.DP_EntrezGene_Info e
where h.hsymbol = e.symbol and e.taxID = 9606)
go

create index results_idx1 on #results(hstatus)
go

print ''
print 'Interim Markers'
print '(sorted by human symbol status (if applicable) and date)'
print ''

select msymbol as "Mouse Symbol", 
       hstatus as "Status", 
       hsymbol as "Human Symbol", 
       name as "Mouse Name", 
       creation_date
from #results
order by hstatus desc, creation_date
go

