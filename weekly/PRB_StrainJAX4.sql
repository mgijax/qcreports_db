
\echo ''
\echo 'New JRs created in past week'
\echo ''

select substring(a.accID,1,8) as accID, substring(s.strain,1,70) as strain
from ACC_Accession a, PRB_Strain s
where a._MGIType_key = 10
and a._LogicalDB_key = 22
and a.creation_date between (now() + interval '-7 day') and now()
and a._Object_key = s._Strain_key
order by a.accID
;

