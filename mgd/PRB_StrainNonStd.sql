print ""
print "Strains - Non Standard"
print ""

select strain from PRB_Strain
where standard = 0
order by strain
go

