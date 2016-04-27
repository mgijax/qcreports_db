\echo ''
\echo 'QTL Public Reference Notes'
\echo ''

select distinct e.exptType as QTL_Expperiment_Type, 
e.jnumID as Reference_Note_Jnumber, 
substring(n.note,1,100) as Reference_Note
from MLD_Expt_View e, MLD_Notes n
where e.exptType in ('TEXT-QTL') 
and e._Refs_key and = n._Refs_key
and n.note ilike '%' 
order by e.exptType, e.jnumID
;

