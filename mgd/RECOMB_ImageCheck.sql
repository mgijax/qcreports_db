
set nocount on

/* select all Gel Assays with Image Panes that have JPGs (xDim is not null) */

select distinct a._Assay_key, a._ImagePane_key, ip._Image_key
into #assays 
from GXD_Assay a, IMG_Image i, IMG_ImagePane ip 
where a._AssayType_key in (10,11)
and a._ImagePane_key = ip._ImagePane_key 
and ip._Image_key = i._Image_key 
and i.xDim is not null
go

/* select all InSitu Assays with Image Panes that have JPGs (xDim is not null) */

insert into #assays 
select distinct s._Assay_key, iri._ImagePane_key, ip._Image_key
from GXD_InSituResultImage iri, GXD_InSituResult r, GXD_Specimen s, GXD_Assay a, IMG_Image i, IMG_ImagePane ip 
where iri._ImagePane_key = ip._ImagePane_key 
and ip._Image_key = i._Image_key 
and i.xDim is not null 
and iri._Result_key = r._Result_key 
and r._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (10,11)
go

create index idx1 on #assays(_ImagePane_key)
go

set nocount off

print ''
print 'Thumbnails with JPGs'
print ''

select distinct c.accID as 'MGI ID'
from #assays aa, IMG_Image a, IMG_Image b, ACC_Accession c
where a._MGIType_key = 8 
and a._ImageType_key = 1072158
and a.xDim is not null
and a._Image_key = aa._Image_key
and a._ThumbnailImage_key = b._Image_key
and b.xDim is not null
and b._Image_key = c._Object_key
and c._MGIType_key = 9
and c._LogicalDB_key = 1
and c.prefixPart = 'MGI:'
order by accID
go

