
print ""
print "JPGs but no Copyright Statement"
print ""

select i.mgiID , jnumID
from IMG_Image_View i 
where i._MGIType_key = 8
and i._ImageType_key = 1072158
and i.xDim is not null
and i.yDim is not null 
and _Image_key not in
(select distinct i._Image_key
from IMG_Image i, MGI_Note mn, MGI_NoteChunk mnc
where i._Image_key = mn._Object_key
and mn._MGIType_key = 9
and mn._NoteType_key = 1023
and mn._Note_key = mnc._Note_key)
go

