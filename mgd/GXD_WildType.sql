
print ""
print "Genotypes where Allele 1 is 'wild type'"
print ""

select ga.accID, strain = substring(g.strain, 1, 50), a.symbol
from GXD_Genotype_Acc_View ga, GXD_Genotype_View g, GXD_AllelePair ap, ALL_Allele a
where g._Genotype_key = ap._Genotype_key
and ap._Allele_key_1 = a._Allele_key
and a.name = 'wild type'
and g._Genotype_key = ga._Object_key
go
