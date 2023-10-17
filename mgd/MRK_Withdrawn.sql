
\echo ''
\echo 'Withdrawals Processed within 3 days'
\echo ''

select substring(history,1,30) as "Old Symbol", 
substring(symbol,1,30) as "New Symbol", 
substring(markerName,1,50) as "New Name",
to_char(event_date, 'MM/dd/yyyy') as "Event Date"
from MRK_History_View
where _Marker_Event_key in (106563605, 106563606, 106563607, 106563608, 106563609)
and event_date >= (now() + interval '-3 day') and event_date <= now()
order by symbol
;

