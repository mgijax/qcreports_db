print ""
print "Cell Lines"
print ""

select distinct term
from VOC_Term_CellLine_View
order by term
go

