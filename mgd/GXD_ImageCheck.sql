
print ""
print "GXD Image Figure Labels Beginning 'Fig%' or ending '%.'"
print ""

select distinct i.jnumID + ";" + i.figureLabel
from IMG_Image_View i
where i.figureLabel like "Fig%"
or i.figureLabel like "%."
order by i.jnum
go

print ""
print "GXD Images with Copyright containing '*'"
print ""

select distinct i.jnumID + ";" + i.figureLabel
from IMG_Image_View i
where i.copyrightNote like "%*%"
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
print "GXD Image Pane Labels Without at least One Field Type Specified"
print ""

select distinct i.jnumID + ";" + i.figureLabel
from IMG_Image_View i
where not exists (select 1 from IMG_ImagePane p
where i._Image_key = p._Image_key)
order by i.jnum
go

