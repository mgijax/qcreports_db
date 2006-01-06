
set nocount on
go

/* exclude cDNA (74725) and primer extension (74728) */

select _Index_key
into #singles
from GXD_Index_Stages
group by _Index_key having count(*) = 1
go

create index idx1 on #singles(_Index_key)
go

select s._Index_key
into #excluded
from #singles s, GXD_Index_Stages gs
where s._Index_key = gs._Index_key
and gs._IndexAssay_key in (74725, 74728)
go

create index idx1 on #excluded(_Index_key)
go

set nocount off
go

print ""
print "Full Coded References that contain indexed Genes that have not been full coded"
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

