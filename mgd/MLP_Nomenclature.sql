print ''
print 'Strains Affected by Recent Nomenclature Changes'
print ''
print 'These Strains have their ''Needs Review - nomen'' flag set to ''Yes''.'
print 'To remove a Strain from this report, set the flag to ''No''.'
print ''

select substring(s.strain,1,60) as strain, 
       substring(m.symbol,1,25) as marker, 
       substring(a.symbol,1,25) as allele,
       s.modification_date
from PRB_Strain s
     INNER JOIN PRB_Strain_NeedsReview_View n on (s._Strain_key = n._Object_key
	and n.term = 'Needs Review - nomen')
     LEFT OUTER JOIN PRB_Strain_Marker sm on (s._Strain_key = sm._Strain_key)
     LEFT OUTER JOIN MRK_Marker m on (sm._Marker_key = m._Marker_key)
     LEFT OUTER JOIN ALL_Allele a on (sm._Allele_key = a._Allele_key)
order by s.modification_date desc, strain
go

