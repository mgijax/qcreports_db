print ""
print "Strains - Non Standard - Sorted by Creation Date"
print ""

select strain = substring(strain, 1, 75), creation_date from PRB_Strain
where standard = 0
order by creation_date desc, strain
go

