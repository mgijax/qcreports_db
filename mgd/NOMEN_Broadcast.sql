select _Nomen_key
INTO TEMPORARY TABLE nomen
from NOM_Marker
where broadcast_date between (now() + interval '-3 day') and now()
;

\echo ''
\echo 'Nomenclature Symbols Broadcast Within Last 3 Days'
\echo ''

select v.symbol, substring(v.name, 1, 50) as name, substring(v.status,1,25) as status, 
v.chromosome, v.createdBy, v.broadcastBy, r.jnumID, 
to_char(v.broadcast_date, 'MM/dd/yyyy') as "broadcast date"
from nomen n, NOM_Marker_View v, MGI_Reference_Nomen_View r
where n._Nomen_key = v._Nomen_key
and v._Nomen_key = r._Object_key
and r.assocType = 'Primary'
order by v.broadcastBy, v.broadcast_date, v.createdBy
;
