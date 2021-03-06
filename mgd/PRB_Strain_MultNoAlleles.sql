select distinct s._Strain_key, substring(s.strain,1,85) as strain, 
sm.symbol, sm._Marker_key, sm._Allele_key
INTO TEMPORARY TABLE strains
from PRB_Strain s, VOC_Annot st, PRB_Strain_Marker_View sm
where s.strain like '%>'
and s._Strain_key = st._Object_key
and st._AnnotType_key = 1009
and st._Term_key in (481370,481371,481383)
and s._Strain_key = sm._Strain_key
;

select _Strain_key
INTO TEMPORARY TABLE multiples
from strains
group by _Strain_key having count(*) > 1
;

\echo ''
\echo 'Strains ending with ''>'''
\echo 'with Strain Attribute of mutant stock, mutant strain or targeted mutation '
\echo 'with Multiple Markers and at least one Marker has no Alleles'
\echo ''

select distinct s.strain, s.symbol
from multiples m, strains s
where m._Strain_key = s._Strain_key
and s._Allele_key is null
order by s.strain
;

