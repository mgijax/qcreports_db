
\echo ''
\echo 'Alleles of type Targeted or Gene Trap that have no MCL association'
\echo ''

select a.symbol
from ALL_Allele a
where a._Allele_Type_key in (847116,847121)
and not exists (select 1 from ALL_Allele_Cellline c
	where a._Allele_key = c._Allele_key)
order by a.symbol

;

