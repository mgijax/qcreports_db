print ""
print "Strains - Standard"
print ""

select strain from PRB_Strain
where standard = 1
order by strain
go

