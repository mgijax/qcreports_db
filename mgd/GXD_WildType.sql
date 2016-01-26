/* TR12057 include only MGI IDs */

\echo ''
\echo 'Genotypes where Allele 1 is ''wild type'''
\echo ''

select ga.accID, substring(g.strain, 1, 50) as strain, a.symbol
from ACC_Accession ga, GXD_Genotype_View g, GXD_AllelePair ap, ALL_Allele a
where g._Genotype_key = ap._Genotype_key
and ap._Allele_key_1 = a._Allele_key
and a.isWildType = 1
and g._Genotype_key = ga._Object_key
and ga._MGIType_key = 12
and ga._LogicalDB_key = 1
;
