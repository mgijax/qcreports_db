print ""
print "Duplicate Strains"
print ""

select strain from PRB_Strain
group by strain having count(*) > 1
order by strain
go

