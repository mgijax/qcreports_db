print ""
print "ES Cell Line Strains Modified Last Month - Sorted by Modification Date"
print ""

select distinct mgiID = ac.accID, e.cellLine, s.strain, s.modification_date
from ALL_Allele a, ACC_Accession ac, ALL_CellLine e, PRB_Strain s
where e._Strain_key = s._Strain_key
and datepart(year, s.modification_date) = datepart(year, getdate())
and datepart(month, s.modification_date) = datepart(month, getdate()) - 1
and e._CellLine_key != -2
and e._CellLine_key = a._ESCellLine_key
and a._Allele_key = ac._Object_key
and ac._MGIType_key = 11
and ac._LogicalDB_key = 1
and ac.prefixPart = "MGI:"
and ac.preferred = 1
order by s.modification_date desc, s.strain

go

