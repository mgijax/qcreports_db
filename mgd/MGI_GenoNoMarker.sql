
\echo ''
\echo 'Genotype Alleles that Contain No Markers'
\echo ''

select distinct aa.symbol
        from GXD_AlleleGenotype g, ALL_Allele aa
        where g._Allele_key = aa._Allele_key
        and aa._Marker_key is null
;

