
print ""
print "Genotypes where Allele 1 is 'wild type'"
print ""

select strain = substring(g.strain, 1, 50), a.symbol
from GXD_Genotype_View g, GXD_AllelePair ga, ALL_Allele a
where g._Genotype_key = ga._Genotype_key
and ga._Allele_key_1 = a._Allele_key
and a.name = 'wild type'
go
