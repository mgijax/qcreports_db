\echo ''
\echo 'HT Sample Hemizygous Genotype Check'
\echo 'genotypes that have 2 alleles and pair state = heterozygous or homozygous'
\echo 'mutated gene on X or Y'
\echo 'sex = male'
\echo ''

select a1.accID as exptID, s.name, s._sex_key, ap._pairstate_key
from GXD_HTSample s, ACC_Accession a1, GXD_AllelePair ap, MRK_Marker m
where s._sex_key = 315165
and s._Experiment_key = a1._Object_key
and a1._MGIType_key = 42
and a1._LogicalDB_key in (189, 190)
and s._genotype_key = ap._genotype_key
and ap._pairstate_key in (847137,847138)
and ap._marker_key = m._marker_key
--and m.chromosome in ('X', 'Y')
group by 1,2,3,4 having count(*) = 2
;

