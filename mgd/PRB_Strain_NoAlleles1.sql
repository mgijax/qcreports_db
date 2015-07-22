select distinct s._Strain_key, substring(s.strain,1,85) as strain,
substring(strain, charindex('-', strain) + 1, char_length(s.strain)) as alleleSymbol,
sm.symbol, sm._Marker_key, sm._Allele_key
INTO TEMPORARY TABLE strains
from PRB_Strain s, PRB_Strain_Marker_View sm
where s.strain like '%<%>%'
and s._Strain_key = sm._Strain_key
;

\echo ''
\echo 'Strains containing ''<>'' '
\echo 'with any number of Markers and Marker has no Allele'
\echo 'and Allele symbol embedded in Strain is in MGD'
\echo ''

select s.strain, s.symbol, substring(s.alleleSymbol, 1, 35) as alleleSymbol
from strains s
where s._Allele_key is null
and exists (select 1 from ALL_Allele a
where s._Marker_key = a._Marker_key
and lower(s.alleleSymbol) = lower(a.symbol))
order by s.strain
;

