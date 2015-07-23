select distinct s._Strain_key, substring(s.strain,1,50) as strain, s.private,
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
\echo 'Private Strains ending with >'
\echo 'with Strain Attribute of mutant stock, mutant strain or targeted mutation '
\echo 'with at most one Marker and Marker has no Allele'
\echo 'and Allele symbol is *not* in MGD'
\echo ''

select substring(l.name, 1, 20) as externalDB, a.accID, s.strain, s.symbol, 
substring(s.alleleSymbol, 1, 35) as alleleSymbol
from singles ss, strains s, ACC_Accession a, ACC_LogicalDB l
where ss._Strain_key = s._Strain_key
and s._Allele_key is null
and s.private = 1
and s._Strain_key = a._Object_key
and a._MGIType_key = 10
and a._LogicalDB_key != 1
and a._LogicalDB_key = l._LogicalDB_key
and not exists (select 1 from ALL_Allele a
where s._Marker_key = a._Marker_key
and s.alleleSymbol = a.symbol)
order by s.strain
;

\echo ''
\echo 'Public Strains ending with > '
\echo 'with Strain Attribute of mutant stock, mutant strain or targeted mutation '
\echo 'with at most one Marker and Marker has no Allele'
\echo 'and Allele symbol is *not* in MGD'
\echo ''

select substring(l.name, 1, 20) as externalDB, a.accID, s.strain, s.symbol, 
substring(s.alleleSymbol, 1, 35) as alleleSymbol
from singles ss, strains s, ACC_Accession a, ACC_LogicalDB l
where ss._Strain_key = s._Strain_key
and s._Allele_key is null
and s.private = 0
and s._Strain_key = a._Object_key
and a._MGIType_key = 10
and a._LogicalDB_key != 1
and a._LogicalDB_key = l._LogicalDB_key
and not exists (select 1 from ALL_Allele a
where s._Marker_key = a._Marker_key
and s.alleleSymbol = a.symbol)
order by s.strain
;

