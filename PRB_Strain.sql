print ""
print "Strains excluding F1s"
print ""

select strain from PRB_Strain
where strain not like '%)F1%'
order by strain
go

print ""
print "F1 Strains Only"
print ""

select strain from PRB_Strain
where strain like '%)F1%'
order by strain
go

