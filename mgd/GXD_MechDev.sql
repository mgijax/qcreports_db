set nocount on
go

/* get set of references not coded */

select distinct i._Refs_key
into #refs
from GXD_Index i, GXD_Index_Stages s, BIB_Refs b, VOC_Term_GXDIndexAssay_View a
where i._Refs_key = b._Refs_key
and b.journal = "Mech Dev"
and i._Index_key =  s._Index_key
and s._IndexAssay_key = a._Term_key
and a.term in ("Northern", "Western", "RT-PCR", "RNAse prot", "Prot-sxn", "RNA-sxn", "Prot-WM", "RNA-WM", "Primer ex", "cDNA")
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
go

select distinct i._Refs_key
into #todelete
from #refs r, GXD_Index i, GXD_Index_Stages s, 
VOC_Term_GXDIndexStage_View g, VOC_Term_GXDIndexAssay_View a
where r._Refs_key = i._Refs_key
and i._Index_key = s._Index_key
and s._StageID_key = g._Term_key
and g.term = "E"
and s._IndexAssay_key = a._Term_key
and a.term = "Northern"
union
select distinct i._Refs_key
from #refs r, GXD_Index i, GXD_Index_Stages s, 
VOC_Term_GXDIndexStage_View g, VOC_Term_GXDIndexAssay_View a
where r._Refs_key = i._Refs_key
and i._Index_key = s._Index_key
and s._StageID_key = g._Term_key
and g.term = "E"
and s._IndexAssay_key = a._Term_key
and a.term = "Western"
union
select distinct i._Refs_key
from #refs r, GXD_Index i, GXD_Index_Stages s, 
VOC_Term_GXDIndexStage_View g, VOC_Term_GXDIndexAssay_View a
where r._Refs_key = i._Refs_key
and i._Index_key = s._Index_key
and s._StageID_key = g._Term_key
and g.term = "E"
and s._IndexAssay_key = a._Term_key
and a.term = "RT-PCR"
union
select distinct i._Refs_key
from #refs r, GXD_Index i, GXD_Index_Stages s, 
VOC_Term_GXDIndexStage_View g, VOC_Term_GXDIndexAssay_View a
where r._Refs_key = i._Refs_key
and i._Index_key = s._Index_key
and s._StageID_key = g._Term_key
and g.term = "E"
and s._IndexAssay_key = a._Term_key
and a.term = "RNAse prot"
union
select distinct i._Refs_key
from #refs r, GXD_Index i, GXD_Index_Stages s, 
VOC_Term_GXDIndexStage_View g, VOC_Term_GXDIndexAssay_View a
where r._Refs_key = i._Refs_key
and i._Index_key = s._Index_key
and s._StageID_key = g._Term_key
and g.term in ("E", "A")
and s._IndexAssay_key = a._Term_key
and a.term = "Prot-sxn"
union
select distinct i._Refs_key
from #refs r, GXD_Index i, GXD_Index_Stages s, 
VOC_Term_GXDIndexStage_View g, VOC_Term_GXDIndexAssay_View a
where r._Refs_key = i._Refs_key
and i._Index_key = s._Index_key
and s._StageID_key = g._Term_key
and g.term in ("E", "A")
and s._IndexAssay_key = a._Term_key
and a.term = "RNA-sxn"
union
select distinct i._Refs_key
from #refs r, GXD_Index i, GXD_Index_Stages s, 
VOC_Term_GXDIndexStage_View g, VOC_Term_GXDIndexAssay_View a
where r._Refs_key = i._Refs_key
and i._Index_key = s._Index_key
and s._StageID_key = g._Term_key
and g.term in ("E", "A")
and s._IndexAssay_key = a._Term_key
and a.term = "Prot-WM"
union
select distinct i._Refs_key
from #refs r, GXD_Index i, GXD_Index_Stages s, 
VOC_Term_GXDIndexStage_View g, VOC_Term_GXDIndexAssay_View a
where r._Refs_key = i._Refs_key
and i._Index_key = s._Index_key
and s._StageID_key = g._Term_key
and g.term in ("E", "A")
and s._IndexAssay_key = a._Term_key
and a.term = "RNA-WM"
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
print "Reference and Number of Markers Analyzed for Journal: Mech Dev"
print ""

select distinct a.accID, i.markerCount
from #mcount i, BIB_Acc_View a
where i._Refs_key = a._Object_key
and a.prefixPart = "J:"
order by markerCount desc
go

set nocount on
go

/* get set of references not coded */
/* and marker contains no expression */

select distinct i._Refs_key
into #refs2
from GXD_Index i, GXD_Index_Stages s, BIB_Refs b
where i._Refs_key = b._Refs_key
and b.journal = "Mech Dev"
and i._Index_key = s._Index_key
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
and not exists (select 1 from GXD_Assay a where i._Marker_key = a._Marker_key)
go

