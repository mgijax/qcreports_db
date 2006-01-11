
set nocount on
go

/* exclude cDNA (74725) and primer extension (74728) */

select distinct gi._Index_key
into #excluded
from GXD_Index gi, GXD_Index_Stages gs 
where gi._Index_key = gs._Index_key
and gs._IndexAssay_key in (74725, 74728)
and not exists (select 1 from GXD_Index_Stages gs2
where gi._Index_key = gs2._Index_key
and gs2._IndexAssay_key not in (74725, 74728))
go

/* exclude E? */

insert into #excluded
select distinct gi._Index_key
from GXD_Index gi, GXD_Index_Stages gs 
where gi._Index_key = gs._Index_key
and gs._StageID_key = 74769
and not exists (select 1 from GXD_Index_Stages gs2
where gi._Index_key = gs2._Index_key
and gs2._StageID_key != 74769)
go

insert into #excluded
select _Index_key from GXD_Index
where comments like '%ot blot%'
or comments like '%fraction%'
or comments like '%reverse%'
go

create index idx1 on #excluded(_Index_key)
go

set nocount off
go

print ""
print "Full Coded References that contain indexed Genes that have not been full coded"
print ""
print "excluded:"
print "     index records that contain only cDNA or primer extension assays"
print "     index records that contain age 'E?'"
print "     index records that have a note that contains 'ot blot', 'fraction', or 'reverse'"
print ""

select distinct b.accID, m.symbol
from GXD_Index i, MRK_Marker m, ACC_Accession b
where not exists (select 1 from #excluded e where i._Index_key = e._Index_key)
and exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key
and i._Marker_key = a._Marker_key)
and i._Marker_key = m._Marker_key
and i._Refs_key = b._Object_key
and b._MGIType_key = 1
and b._LogicalDB_key = 1
and b.prefixPart = "J:"
order by b.numericPart
go

