print ""
print "Unique Tissue/Cell Line Pairs"
print ""

select distinct t.tissue, cellLine = vt.term
from PRB_Source s, PRB_Tissue t, VOC_Term vt
where s._Tissue_key = t._Tissue_key
and t.tissue != "Not Specified"
and s._CellLine_key = vt._Term_key
and vt.term != "Not Specified"
order by t.tissue
go

