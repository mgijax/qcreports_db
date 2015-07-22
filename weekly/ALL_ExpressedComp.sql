\echo ''
\echo 'Allele Missing Expressed Component Attribute'
\echo ''

select substring(a1.accID,1, 15) as alleleID, aa.symbol as alleleSymbol, substring(a2.accID, 1, 15) as markerID, m.symbol as markerSymbol
from MGI_Relationship r, ACC_Accession a1, ALL_Allele aa, ACC_Accession a2, MRK_Marker m
where r._Category_key = 1004
and r._Object_key_1 = a1._Object_key
and a1._MGIType_key = 11
and a1._LogicalDB_key = 1
and a1.preferred = 1
and r._Object_key_1 = aa._Allele_key
and r._Object_key_2 = a2._Object_key
and a2._MGIType_key = 2
and a2._LogicalDB_key = 1
and a2.preferred = 1
and r._Object_key_2 = m._Marker_key
and not exists(select 1
from VOC_Annot v
where v._AnnotType_key = 1014
and r._Object_key_1 = v._Object_key
and v._Term_key = 11025597)
go
