set nocount on
go

/* get set of references not coded with high priority */

select distinct i._Refs_key, i._Marker_key
into #markers
from GXD_Index i, BIB_Refs b, VOC_Term_GXDIndexPriority_View a
where i._Refs_key = b._Refs_key
and b.journal = "Mech Dev"
and i._Priority_key =  a._Term_key
and a.term = "High"
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
go

select m.*, markerCount = count(*) 
into #mcount
from #markers m
group by _Refs_key
go

set nocount off
go

print ""
print "Reference and Number of Markers Analyzed for Journal: Mech Dev"
print ""

select distinct a.accID, i.markerCount
from #mcount i, ACC_Accession a
where i._Refs_key = a._Object_key
and a._MGIType_key = 1
and a.prefixPart = "J:"
order by markerCount desc
go

set nocount on
go

drop table #markers
go

drop table #mcount
go

/* get set of references/markers not coded with high priority */

select distinct i._Refs_key, i._Marker_key
into #markers
from GXD_Index i, BIB_Refs b, VOC_Term_GXDIndexPriority_View a
where i._Refs_key = b._Refs_key
and b.journal = "Mech Dev"
and i._Priority_key =  a._Term_key
and a.term = "High"
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
and not exists (select 1 from GXD_Assay a where i._Marker_key = a._Marker_key)
go

select m.*, markerCount = count(*) 
into #mcount
from #markers m
group by _Refs_key
go

set nocount off
go

print ""
print "Mech Dev: Papers with New Genes"
print ""

select distinct a.accID, i.markerCount
from #mcount i, ACC_Accession a
where i._Refs_key = a._Object_key
and a._MGIType_key = 1
and a.prefixPart = "J:"
order by markerCount desc
go

