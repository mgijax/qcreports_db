print ""
print "Strains Affected by recent Nomenclature changes"
print ""

select strain 
from PRB_Strain 
where needsReview = 1
order by strain
go

