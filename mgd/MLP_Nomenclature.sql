print ""
print "Strains Affected by Recent Nomenclature Changes"
print ""
print "These Strains have their 'Needs Review' flag set to 'Yes'."
print "To remove a Strain from this report, set the flag to 'No'."
print ""

select s.strain 
from PRB_Strain s, PRB_Strain_NeedsReview_View n
where s._Strain_key = n._Strain_key
and n.term = "Needs Review - nomen"
order by s.strain
go

