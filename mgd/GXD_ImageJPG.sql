
set nocount on
go

/* select all Gel Assays with Image Panes that have JPGs (xDim is not null) */
/* exclude J:80502 */

select distinct a._Assay_key, a._AssayType_key, i._Refs_key, a._ImagePane_key, ip._Image_key
into #assays 
from GXD_Assay a, IMG_Image i, IMG_ImagePane ip 
where a._ImagePane_key = ip._ImagePane_key 
and ip._Image_key = i._Image_key 
and i.xDim is not null
and a._Refs_key not in (81463)
go

/* select all InSitu Assays with Image Panes that have JPGs (xDim is not null) */

insert into #assays 
select distinct s._Assay_key, a._AssayType_key, i._Refs_key, iri._ImagePane_key, ip._Image_key
from GXD_InSituResultImage iri, GXD_InSituResult r, GXD_Specimen s, GXD_Assay a, IMG_Image i, IMG_ImagePane ip 
where iri._ImagePane_key = ip._ImagePane_key 
and ip._Image_key = i._Image_key 
and i.xDim is not null 
and iri._Result_key = r._Result_key 
and r._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
go

create index idx1 on #assays(_ImagePane_key)
go

/* select those that are annotated to more than 2 assays */

select * into #final from #assays where _AssayType_key = 6 group by _ImagePane_key having count(*) > 2
union
select * from #assays where _AssayType_key != 6 group by _ImagePane_key having count(*) > 1
go

create index idx1 on #final(_Refs_key)
create index idx2 on #final(_Image_key)
go

set nocount off
go

print ""
print "Displayed Image Panes annotated to >2 assays (if Immunohistochemistry), >1 assay for all others."
print ""

select distinct imageID = i.accID, refID = r.accID 
from #final f, ACC_Accession i, ACC_Accession r  
where f._Image_key = i._Object_key 
and i._MGIType_key = 9 
and i._LogicalDB_key = 1 
and i.prefixPart = "MGI:" 
and i.preferred = 1
and f._Refs_key = r._Object_key 
and r._MGIType_key = 1 
and r._LogicalDB_key = 1 
and r.prefixPart = "J:" 
and r.preferred = 1
order by imageID
go

