
\echo ''
\echo 'Full Coded References that are missing a Gene in the Index'
\echo ''

select distinct b.accID, m.symbol, b.numericPart, u.login
from GXD_Assay a, MRK_Marker m, ACC_Accession b, MGI_User u
where a._AssayType_key in (1,2,3,4,5,6,8,9)
and not exists (select 1 from GXD_Index i
where a._Refs_key = i._Refs_key
and a._Marker_key = i._Marker_key)
and a._Marker_key = m._Marker_key
and a._Refs_key = b._Object_key
and b._MGIType_key = 1
and b._LogicalDB_key = 1
and b.prefixPart = 'J:'
and a._ModifiedBy_key = u._User_key
order by b.numericPart
;

