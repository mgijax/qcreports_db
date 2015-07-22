\echo ''
\echo 'Reference selected for GXD which have been not been used.'
\echo 'Those that have also been statused as ''Never Used'' are so noted.'
\echo ''

select r.jnumID, 
case when isNeverUsed = 1 then 'Never Used' else '' end as catetory
from BIB_All_View r, BIB_DataSet_Assoc dsa, BIB_DataSet ds
where not exists (select 1 from GXD_Assay e
where r._Refs_key = e._Refs_key)
and not exists (select 1 from GXD_Index e
where r._Refs_key = e._Refs_key)
and r._Refs_key = dsa._Refs_key
and dsa._DataSet_key = ds._DataSet_key
and ds.abbreviation = 'Expression'
order by r.jnumID
go
