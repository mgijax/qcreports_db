print ""
print "Strains - Standard (excluding F1s and F2s)"
print ""

select strain from PRB_Strain
where standard = 1
and strain not like '(%'
and strain not like '%)F1'
and strain not like '%)F2'
order by strain
go

