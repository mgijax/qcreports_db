
\echo ''
\echo 'Withdrawals Processed within 3 days'
\echo ''

select substring(history,1,30) as "Old Symbol", 
substring(symbol,1,30) as "New Symbol", 
substring(markerName,1,50) as "New Name",
convert(char(10), event_date, 101) as "Event Date"
from MRK_History_View
where _Marker_Event_key in (2,3,4,5,6)
and event_date >= dateadd(day, -3, getdate()) and event_date <= getdate()
order by symbol
;

