set nocount on
go

/* get all references, except only clones = 1 */

select distinct i._Refs_key, type = 'blot'
into #refs
from GXD_Index i, GXD_Index_Stages s, BIB_Refs b
where i._Refs_key = b._Refs_key
and b.journal = "Gene Expr Patterns"
and (northern = 1
     or western = 1
     or rt_pcr = 1
     or rnase = 1 
     or nuclease = 1
     or primer_extension =1
)
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
union
select distinct i._Refs_key, type = 'insitu'
from GXD_Index i, GXD_Index_Stages s, BIB_Refs b
where i._Refs_key = b._Refs_key
and b.journal = "Mech Dev"
and (insitu_protein_section = 1
     or insitu_rna_section = 1
     or insitu_protein_mount = 1 
     or insitu_rna_mount = 1
)
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
go

delete #refs
from #refs r, GXD_Index i, GXD_Index_Stages s
where r._Refs_key = i._Refs_key
and r.type = 'blot'
and i.index_id = s.index_id
and s.stage_id = 40
go

delete #refs
from #refs r, GXD_Index i, GXD_Index_Stages s
where r._Refs_key = i._Refs_key
and r.type = 'insitu'
and i.index_id = s.index_id
and s.stage_id in (40,41)
go

select r.*, i._Marker_key
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

