print ""
print "Strains Affected by Recent Nomenclature Changes"
print ""
print "These Strains have their 'Needs Review' flag set to 'Yes'."
print "To remove a Strain from this report, set the flag to 'No'."
print ""

select strain 
from PRB_Strain 
where needsReview = 1
order by strain
go

