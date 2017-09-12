\echo ''
\echo 'Reference where '
\echo 'group = GXD, status in ''Routed'' or ''Chosen'' '
\echo 'if tag, then tag like ''GXD:'' '
\echo ''

(
select 'J:' || r.numericPart as numericPart, wft.term as wfterm
from BIB_Citation_Cache r, BIB_Workflow_Status s, BIB_Workflow_Tag t, VOC_Term wft
where r._Refs_key = s._Refs_key
and s.isCurrent = 1
and s._Group_key = 31576665
and s._Status_key in (31576670, 31576671)
and r._Refs_key = t._Refs_key
and t._Tag_key = wft._Term_key
and wft.term like 'GXD:%'
union
select 'J:' || r.numericPart as numericPart, null as wfterm
from BIB_Citation_Cache r, BIB_Workflow_Status s
where r._Refs_key = s._Refs_key
and s.isCurrent = 1
and s._Group_key = 31576665
and s._Status_key in (31576670, 31576671)
and not exists (select 1 from BIB_Workflow_Tag t, VOC_Term wft
	where r._Refs_key = t._Refs_key
	and t._Tag_key = wft._Term_key
	and wft.term like 'GXD:%'
	)
)
order by wfterm, numericPart
;
