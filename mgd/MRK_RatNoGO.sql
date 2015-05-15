
set nocount on
go

select m._Marker_key, m._Organism_key, m.symbol, substring(m.name,1,100) as name
into #markers1
from MRK_Marker m
where m._Organism_key = 1
and m._Marker_Type_key = 1
and m._Marker_Status_key in (1,3)
and not exists (select 1 from VOC_Annot g
where g._AnnotType_key = 1000
and m._Marker_key = g._Object_key)
go

create index markers1_idx on #markers1(_Marker_key)
go

select m.*, a.accID
into #markers2
from #markers1 m, ACC_Accession a
where m._Marker_key = a._Object_key
and a._MGIType_key = 2
and a.prefixPart = 'MGI:'
and a._LogicalDB_key = 1
and a.preferred = 1
go

create index markers2_idx on #markers2(_Marker_key)
go

select distinct m.accID, m.symbol, m.name
into #markersA
from #markers2 m, MRK_Cluster mc, MRK_ClusterMember hm1, MRK_ClusterMember hm2, MRK_Marker m2
where mc._ClusterSource_key = 9272151
and mc._Cluster_key = hm1._Cluster_key
and m._Marker_key = hm1._Marker_key
and hm1._Cluster_key = hm2._Cluster_key
and hm2._Marker_key = m2._Marker_key
and m2._Organism_key = 40
go

select distinct m.accID, m.symbol, m.name
into #markersB
from #markers2 m, MRK_Cluster mc, MRK_ClusterMember hm1, MRK_ClusterMember hm2, MRK_Marker m2
where mc._ClusterSource_key = 9272151
and mc._Cluster_key = hm1._Cluster_key
and m._Marker_key = hm1._Marker_key
and hm1._Cluster_key = hm2._Cluster_key
and hm2._Marker_key = m2._Marker_key
and m2._Organism_key = 2
and not exists (select 1 from MRK_ClusterMember hm3, MRK_Marker m3
where hm1._Cluster_key = hm3._Cluster_key
and hm3._Marker_key = m3._Marker_key
and m._Organism_key = 2
and m3._Organism_key not in (1,2))
go

print ''
print 'Mouse Genes that have Rat Homologs but no GO associations'
print ''

select 'Number of unique MGI Gene IDs:  ', count(distinct accID) from #markersA
union
select 'Number of total rows:  ', count(*) from #markersA
go

print ''

select * from #markersA order by symbol
go

print ''
print 'Mouse Genes that have Human Homologs Only but no GO associations'
print ''

select 'Number of unique MGI Gene IDs:  ', count(distinct accID) from #markersB
union
select 'Number of total rows:  ', count(*) from #markersB
go

print ''

select * from #markersB order by symbol
go

