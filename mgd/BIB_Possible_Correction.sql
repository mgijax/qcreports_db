\echo ''
\echo 'Possible Correction/Retraction'
\echo ''

select c.mgiid
from BIB_Citation_Cache c
where exists (select 1 from BIB_Workflow_Tag t where c._refs_key = t._refs_key and _tag_key = 115722477)
order by mgiid
;
 
