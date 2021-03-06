
\echo ''
\echo 'Hemizygous Genotype Check'
\echo ''

/* genotypes that have 2 alleles and pair state = heterozygous or homozygous and chromosome is X or Y */

select g._Genotype_key, a.name
INTO TEMPORARY TABLE genotypes
from GXD_AllelePair g, ALL_Allele a, MRK_Marker m
where g._PairState_key in (847137, 847138)
and g._Allele_key_2 is not null
and g._Allele_key_1 = a._Allele_key
and a._Marker_key = m._Marker_key
and m.chromosome in ('X','Y')
;

create index genotypes_idx on genotypes(_Genotype_key)
;

\echo ''
\echo 'specimens'
\echo 'genotypes that have 2 alleles and pair state = heterozygous or homozygous'
\echo 'mutated gene on X or Y'
\echo 'sex = male'
\echo ''

select distinct a1.accID as "J number of assay", 
a2.accID as "MGI ID of assay", 
substring(g.name, 1, 30) as "name of allele1 of genotype", a1.numericPart
from genotypes g, GXD_Assay a, GXD_Specimen s, ACC_Accession a1, ACC_Accession a2
where g._Genotype_key = s._Genotype_key
and s.sex = 'Male'
and s._Assay_key = a._Assay_key
and a._AssayType_key in (10,11)
and a._Refs_key = a1._Object_key
and a1._MGIType_key = 1
and a1.prefixPart = 'J:'
and s._Assay_key = a2._Object_key
and a2._MGIType_key = 8
order by a1.numericPart
;

