
/* TR 9938: mismatch of marker type for an alleleand for allele pair */
/* all allele pairs that are attached to different markers */
/* TR12057 include only MGI IDs */

\echo ''
\echo 'Genotypes where Allele Pairs are associated with different Markers'
\echo ''

select a.accID, a1.symbol, a2.symbol, m1.symbol, m2.symbol
from GXD_AllelePair g, 
     ALL_Allele a1, ALL_Allele a2, 
     MRK_Marker m1, MRK_Marker m2,
     ACC_Accession a
where g._Allele_key_1 = a1._Allele_key
and a1._Marker_key = m1._Marker_key
and g._Allele_key_2 = a2._Allele_key
and a2._Marker_key = m2._Marker_key
and m1.symbol != m2.symbol
and g._Genotype_key = a._Object_key
and a._MGIType_key = 12
and a._LogicalDB_key = 1
;

