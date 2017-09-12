
\echo ''
\echo 'Papers ''Routed'' or ''Chosen'' For Expression in past week '
\echo 'by Data Set creation date'
\echo ''

 
select 'J:' || c.numericPart, c.short_citation
from BIB_Refs r, BIB_Citation_Cache c, BIB_Workflow_Status s
where r.creation_date between (now() + interval '-7 day') and now()
and r._Refs_key = s._Refs_key
and s.isCurrent = 1 
and s._Group_key = 31576665
and s._Status_key in (31576670, 31576671)
and r._Refs_key = c._Refs_key
order by c.numericPart
;

