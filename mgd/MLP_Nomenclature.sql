print ""
print "Strains Affected by Recent Nomenclature Changes"
print ""
print "These Strains have their 'Needs Review' flag set to 'Yes'."
print "To remove a Strain from this report, set the flag to 'No'."
print ""

select substring(s.strain,1,60) "strain", 
       substring(m.symbol,1,25) "marker", 
       substring(a.symbol,1,25) "allele",
       s.modification_date
from PRB_Strain s, PRB_Strain_NeedsReview_View n, PRB_Strain_Marker sm,
     MRK_Marker m, ALL_Allele a
where s._Strain_key = n._Strain_key
and s._Strain_key *= sm._Strain_key
and sm._Marker_key *= m._Marker_key
and sm._Allele_key *= a._Allele_key
and n.term = "Needs Review - nomen"
order by s.modification_date desc, strain
go

