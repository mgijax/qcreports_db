
\echo ''
\echo 'References which have GXD Annotations to ''Not Applicable'' Genotype (MGI:2166309)'
\echo ''

select b.accID
from ACC_Accession a, GXD_Expression ge, ACC_Accession b, GXD_Assay ga, MGI_User u
where a.accID = 'MGI:2166309'
and a._Object_key = ge._Genotype_key
and ge._Refs_key = b._Object_key
and b._MGIType_key = 1
and b.prefixPart = 'J:'
and ge._Assay_key = ga._Assay_key
and ga._Modifiedby_key = u._User_key
;
