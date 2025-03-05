\echo ''
\echo 'Gel rows with no Gel bands'
\echo ''
select a.accid, r.*
from acc_accession a, gxd_gelrow r
where not exists (select 1 from gxd_gelband b where r._gelrow_key = b._gelrow_key)
and r._assay_key = a._object_key
and a._mgitype_key = 8;
