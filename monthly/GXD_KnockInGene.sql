select a._Assay_key, a._Refs_key, substring(specimenLabel, 1, 50) as specimenLabel, u.login
INTO TEMPORARY TABLE knockin
from GXD_Assay a, GXD_Specimen s, MGI_User u
where a._AssayType_key = 9
and a._Assay_key = s._Assay_key
and not exists (select 1 from GXD_AlleleGenotype g
where s._Genotype_key = g._Genotype_key
and a._Marker_key = g._Marker_key)
and a._Modifiedby_key = u._User_key
;

\echo ''
\echo 'GXD Knock Ins where the assayed Gene is not the Gene which is mutated in the Genotype'
\echo ''

select a.accID as "Assay", b.accID as "J:", k.specimenLabel, k.login
from knockin k, ACC_Accession a, ACC_Accession b
where k._Assay_key = a._Object_key
and a._MGIType_key = 8
and k._Refs_key = b._Object_key
and b._MGIType_key = 1
and b._LogicalDB_key = 1
and b.prefixPart = 'J:'
;

