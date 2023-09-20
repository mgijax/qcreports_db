\echo ''
\echo 'Strains Affected by Recent Nomenclature Changes'
\echo ''
\echo 'These Strains have their ''Needs Review - nomen'' flag set to ''Yes''.'
\echo 'To remove a Strain from this report, set the flag to ''No''.'
\echo ''

select substring(s.strain,1,60) as strain, 
       substring(m.symbol,1,25) as marker, 
       substring(a.symbol,1,25) as allele,
       array_to_string(array_agg(distinct aa.accid),',') as externalAccId,
       s.modification_date
from PRB_Strain s
     INNER JOIN PRB_Strain_NeedsReview_View n on (s._Strain_key = n._Object_key
	and n.term = 'Needs Review - nomen')
     LEFT OUTER JOIN PRB_Strain_Marker sm on (s._Strain_key = sm._Strain_key)
     LEFT OUTER JOIN MRK_Marker m on (sm._Marker_key = m._Marker_key)
     LEFT OUTER JOIN ALL_Allele a on (sm._Allele_key = a._Allele_key)
     LEFT OUTER JOIN ACC_Accession aa on (s._Strain_key = aa._Object_key and aa._MGIType_key = 10 and aa._LogicalDB_key != 1)
group by s.strain, m.symbol, a.symbol, s.modification_date
order by s.modification_date desc, strain
;

