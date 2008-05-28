
print ""
print "GXD Image Figure Labels Beginning 'Fig'."
print ""

select distinct i.jnumID + ";" + i.figureLabel
from IMG_Image_View i
where i.figureLabel like "Fig%"
order by i.jnum
go

print ""
print "GXD Images with Copyright containing '(||)'"
print ""

select distinct i.jnumID + ";" + i.figureLabel
from IMG_Image_View i, MGI_Note n, MGI_NoteChunk nc
where i._Image_key = n._Object_key
and n._MGIType_key = 12
and n._NoteType_key = 1023
and n._Note_key = nc._Note_key
and nc.note like "%(||)%"
order by i.jnum
go

print ""
print "GXD Image Pane Labels containing ','"
print ""

select distinct i.jnumID + ";" + i.figureLabel
from IMG_Image_View i,IMG_ImagePane p
where p.paneLabel like "%,%" and p._Image_key = i._Image_key
order by i.jnum
go

print ""
print "Elsevier: where the J# in the copyright does not match the J# of the stub"
print ""

select distinct i.jnumID, i.mgiID
from IMG_Image_View i,MGI_Note_Image_View n
where i._MGIType_key = 8
and n._NoteType_key = 1023
and n.note like "reprinted with permission from elsevier%"
and n.note not like "%" + i.jnumID + "%"
and n._Object_key = i._Image_key
order by i.jnumID
go

print ""
print "non-Elsevier: the first author in the copyright does not match the first author in the paper"
print ""

select distinct i.jnumID, i.mgiID, r._primary
from IMG_Image_View i,MGI_Note_Image_View n, BIB_Refs r
where i._MGIType_key = 8
and n._NoteType_key = 1023
and n.note like "this image is from%"
and i._Refs_key = r._Refs_key
and n.note not like "%" + substring(r._primary, 1, charindex(" ", r._primary) - 1) + "%"
and n._Object_key = i._Image_key
order by i.jnumID
go

print ""
print "Images with JPGs whose Thumbnails have no JPGs"
print ""

select distinct c.accID "MGI ID"
from IMG_Image a, IMG_Image b, ACC_Accession c
where a._MGIType_key = 8 
and a._ImageType_key = 1072158
and a.xDim is not null
and a._ThumbnailImage_key = b._Image_key
and b.xDim is null
and a._Image_key = c._Object_key
and c._MGIType_key = 9
and c._LogicalDB_key = 1
and c.prefixPart = "MGI:"
order by accID
go

print ""
print "Images with JPGs whose Thumbnails have JPGs with incorrect X dimension (not = 150 pixels)"
print ""

select distinct c.accID "MGI ID"
from IMG_Image a, IMG_Image b, ACC_Accession c
where a._MGIType_key = 8 
and a._ImageType_key = 1072158
and a.xDim is not null
and a._ThumbnailImage_key = b._Image_key
and b.xDim != 150
and a._Image_key = c._Object_key
and c._MGIType_key = 9
and c._LogicalDB_key = 1
and c.prefixPart = "MGI:"
order by accID
go

