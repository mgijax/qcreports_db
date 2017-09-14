
\echo ''
\echo 'Papers ''Routed'' or ''Chosen'' For Expression in past week by Status creation date'
\echo ''

 
select c.jnumID, c.short_citation, s.creation_date
from BIB_Refs r, BIB_Citation_Cache c, BIB_Workflow_Status s
where s.creation_date between (now() + interval '-7 day') and now()
and r._Refs_key = s._Refs_key
and s.isCurrent = 1 
and s._Group_key = 31576665
and s._Status_key in (31576670, 31576671)
and r._Refs_key = c._Refs_key
order by c.jnumID
;

