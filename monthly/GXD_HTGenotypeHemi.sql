
\echo ''
\echo 'HT Sample Hemizygous Genotype Check'
\echo ''
\echo 'genotypes that have 2 alleles and pair state = heterozygous or homozygous'
\echo 'mutated gene on X or Y'
\echo 'sex = male'
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

create index idx1 on genotypes(_Genotype_key)
;

select distinct a.accID as "Experiment ID", s.name as "Sample Name",
	substring(g.name, 1, 30) as "name of allele1 of genotype"
from genotypes g, ACC_Accession a, GXD_HTSample s
where g._Genotype_key = s._Genotype_key
and s._sex_key = 315165
and s._Experiment_key = a._Object_key
and a._MGIType_key = 42
and a._LogicalDB_key in (189, 190)
and a.preferred = 1
order by a.acciD
;

