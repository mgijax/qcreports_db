print ""
print "ES Cell Line Strains Modified Last Month - Sorted by Modification Date"
print ""

select e.cellLine, s.strain, s.modification_date
from ALL_CellLine e, PRB_Strain s
where e._Strain_key = s._Strain_key
and datepart(year, s.modification_date) = datepart(year, getdate())
and datepart(month, s.modification_date) = datepart(month, getdate()) - 1
order by s.modification_date desc, s.strain
go

