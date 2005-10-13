
print ""
print "GXD Image Figure Labels Beginning 'Fig' or ending '.'"
print ""

select distinct i.jnumID + ";" + i.figureLabel
from IMG_Image_View i
where i.figureLabel like "Fig%"
or i.figureLabel like "%."
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

