set nocount on
go

/* get set of references not coded */

select distinct i._Refs_key
into #refs
from GXD_Index i, GXD_Index_Stages s, BIB_Refs b
where i._Refs_key = b._Refs_key
and b.journal = "Gene Expr Patterns"
and (s.northern = 1
     or s.western = 1
     or s.rt_pcr = 1
     or s.rnase = 1
     or s.insitu_protein_section = 1
     or s.insitu_rna_section = 1
     or s.insitu_protein_mount = 1 
     or s.insitu_rna_mount = 1
     )
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
go

select distinct i._Refs_key
into #todelete
from #refs r, GXD_Index i, GXD_Index_Stages s
where r._Refs_key = i._Refs_key
and i.index_id = s.index_id
and s.stage_id = 40
and s.northern = 1
union
select distinct i._Refs_key
from #refs r, GXD_Index i, GXD_Index_Stages s
where r._Refs_key = i._Refs_key
and i.index_id = s.index_id
and s.stage_id = 40
and s.western = 1
union
select distinct i._Refs_key
from #refs r, GXD_Index i, GXD_Index_Stages s
where r._Refs_key = i._Refs_key
and i.index_id = s.index_id
and s.stage_id = 40
and s.rt_pcr = 1
union
select distinct i._Refs_key
from #refs r, GXD_Index i, GXD_Index_Stages s
where r._Refs_key = i._Refs_key
and i.index_id = s.index_id
and s.stage_id = 40
and s.rnase = 1
union
select distinct i._Refs_key
from #refs r, GXD_Index i, GXD_Index_Stages s
where r._Refs_key = i._Refs_key
and i.index_id = s.index_id
and s.stage_id in (40, 41)
and s.insitu_protein_section = 1
union
select distinct i._Refs_key
from #refs r, GXD_Index i, GXD_Index_Stages s
where r._Refs_key = i._Refs_key
and i.index_id = s.index_id
and s.stage_id in (40, 41)
and s.insitu_rna_section = 1
union
select distinct i._Refs_key
from #refs r, GXD_Index i, GXD_Index_Stages s
where r._Refs_key = i._Refs_key
and i.index_id = s.index_id
and s.stage_id in (40, 41)
and s.insitu_protein_mount = 1 
union
select distinct i._Refs_key
from #refs r, GXD_Index i, GXD_Index_Stages s
where r._Refs_key = i._Refs_key
and i.index_id = s.index_id
and s.stage_id in (40, 41)
and s.insitu_rna_mount = 1
go

delete #refs
from #refs r, #todelete d
where d._Refs_key = r._Refs_key
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
print "Reference and Number of Markers Analyzed for Journal: Gene Expr Patterns"
print ""

select distinct a.accID, i.markerCount
from #mcount i, BIB_Acc_View a
where i._Refs_key = a._Object_key
and a.prefixPart = "J:"
order by markerCount desc
go

