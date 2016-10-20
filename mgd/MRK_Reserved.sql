\echo ''
\echo 'Nomenclature Symbols Within Last 3 Days'
\echo ''

select m.symbol, substring(m.name, 1, 50) as name, 
substring(t.status,1,25) as status, 
m.chromosome, 
u.login,
r.jnumID, 
to_char(m.creation_date, 'MM/dd/yyyy') as "creation date"
from MRK_Marker m, MRK_History h, BIB_Citation_Cache r, MRK_Status t, MGI_User u
where m.creation_date between (now() + interval '-3 day') and now()
and m._Marker_key = h._Marker_key
and h._Marker_key = h._History_key
and h.sequenceNum = 1
and h._Refs_key = r._Refs_key
and m._Marker_Status_key = t._Marker_Status_key
and m._CreatedBy_key = u._User_key
order by u.login, m.creation_date
;
