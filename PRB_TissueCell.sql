print ""
print "Unique Tissue/Cell Line Pairs"
print ""

select distinct t.tissue, s.cellLine
from PRB_Source s, PRB_Tissue t
where s._Tissue_key = t._Tissue_key
and t.tissue != "Not Specified"
and s.cellLine is not null
order by t.tissue
go

