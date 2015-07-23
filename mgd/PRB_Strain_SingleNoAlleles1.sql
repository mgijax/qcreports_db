select distinct s._Strain_key, substring(s.strain,1,85) as strain, 
substring(strain, position('-' in  strain) + 1, char_length(s.strain)) as alleleSymbol,
sm.symbol, sm._Marker_key, sm._Allele_key
INTO TEMPORARY TABLE strains
from PRB_Strain s, VOC_Annot st, PRB_Strain_Marker_View sm
where s.strain like '%>'
and s.strain not like 'STOCK%'
and s._Strain_key = st._Object_key
and st._AnnotType_key = 1009
and st._Term_key in (481370,481371,481383)
and s._Strain_key = sm._Strain_key
;

select _Strain_key
INTO TEMPORARY TABLE singles
from strains
group by _Strain_key having count(*) = 1
;

\echo ''
\echo 'Strains ending with ''>'''
\echo 'with Strain Attribute of mutant stock, mutant strain or targeted mutation '
\echo 'with at most one Marker and Marker has no Allele'
\echo 'and Allele symbol is in MGD'
\echo ''

select s.strain, s.symbol, substring(s.alleleSymbol, 1, 35) as alleleSymbol
from singles ss, strains s, ALL_Allele a
where ss._Strain_key = s._Strain_key
and s._Allele_key is null
and s._Marker_key = a._Marker_key
and s.alleleSymbol = a.symbol
order by s.strain
;

