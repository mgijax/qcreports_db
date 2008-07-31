
print ""
print "JPGs but no Copyright Statement"
print ""

select i.mgiID, i.jnumID
from IMG_Image_View i 
where i._MGIType_key = 8
and i._ImageType_key = 1072158
and i.xDim is not null
and i.yDim is not null 
and not exists
(select 1 from MGI_Note mn
where i._Image_key = mn._Object_key
and mn._MGIType_key = 9
and mn._NoteType_key = 1023)
go

