set nocount on
go

select distinct i._Refs_key
into #refs
from GXD_Index i, GXD_Index_Stages s, BIB_Refs b
where i._Refs_key = b._Refs_key
and b.journal = "Mech Dev"
and s.northern = 1
and s.stage_id != 40
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
union
select distinct i._Refs_key
from GXD_Index i, GXD_Index_Stages s, BIB_Refs b
where i._Refs_key = b._Refs_key
and b.journal = "Mech Dev"
and s.western = 1
and s.stage_id != 40
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
union
select distinct i._Refs_key
from GXD_Index i, GXD_Index_Stages s, BIB_Refs b
where i._Refs_key = b._Refs_key
and b.journal = "Mech Dev"
and s.rt_pcr = 1
and s.stage_id != 40
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
union
select distinct i._Refs_key
from GXD_Index i, GXD_Index_Stages s, BIB_Refs b
where i._Refs_key = b._Refs_key
and b.journal = "Mech Dev"
and s.rnase = 1
and s.stage_id != 40
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
union
select distinct i._Refs_key
from GXD_Index i, GXD_Index_Stages s, BIB_Refs b
where i._Refs_key = b._Refs_key
and b.journal = "Mech Dev"
and s.nuclease = 1
and s.stage_id != 40
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
union
select distinct i._Refs_key
from GXD_Index i, GXD_Index_Stages s, BIB_Refs b
where i._Refs_key = b._Refs_key
and b.journal = "Mech Dev"
and s.primer_extension = 1
and s.stage_id != 40
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
union
select distinct i._Refs_key
from GXD_Index i, GXD_Index_Stages s, BIB_Refs b
where i._Refs_key = b._Refs_key
and b.journal = "Mech Dev"
and s.clones = 1
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
union
select distinct i._Refs_key
from GXD_Index i, GXD_Index_Stages s, BIB_Refs b
where i._Refs_key = b._Refs_key
and b.journal = "Mech Dev"
and insitu_protein_section = 1
and s.stage_id not in (40, 41)
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
union
select distinct i._Refs_key
from GXD_Index i, GXD_Index_Stages s, BIB_Refs b
where i._Refs_key = b._Refs_key
and b.journal = "Mech Dev"
and insitu_rna_section = 1
and s.stage_id not in (40, 41)
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
union
select distinct i._Refs_key
from GXD_Index i, GXD_Index_Stages s, BIB_Refs b
where i._Refs_key = b._Refs_key
and b.journal = "Mech Dev"
and insitu_protein_mount = 1 
and s.stage_id not in (40, 41)
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
union
select distinct i._Refs_key
from GXD_Index i, GXD_Index_Stages s, BIB_Refs b
where i._Refs_key = b._Refs_key
and b.journal = "Mech Dev"
and insitu_rna_mount = 1
and s.stage_id not in (40, 41)
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
go

select distinct r._Refs_key, i._Marker_key
into #markers
from #refs r, GXD_Index i
where r._Refs_key = i._Refs_key
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
from #mcount i, BIB_Acc_View a
where i._Refs_key = a._Object_key
and a.prefixPart = "J:"
order by markerCount desc
go

