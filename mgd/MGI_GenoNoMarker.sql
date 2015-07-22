
\echo ''
\echo 'Genotype Alleles that Contain No Markers'
\echo ''

select distinct aa.symbol
        from GXD_AlleleGenotype g, ALL_Allele aa
        where g._Allele_key = aa._Allele_key
        and not exists (select 1 from ACC_Accession ac
        where g._Marker_key = ac._Object_key 
        and ac._MGIType_key = 2 
        and ac._LogicalDB_key = 1 
        and ac.prefixPart = 'MGI:' 
        and ac.preferred = 1)
;

