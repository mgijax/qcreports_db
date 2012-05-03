
print ''
print 'Alleles of type Targeted or Gene Trap that have no MCL association'
print ''

select a.symbol
from ALL_Allele a
where a._Allele_Type_key in (847116,847117,847118,847119,847120,847121)
and not exists (select 1 from ALL_Allele_Cellline c
	where a._Allele_key = c._Allele_key)
order by a.symbol

go

