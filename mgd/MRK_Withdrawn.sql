declare @startDate char(10)
declare @endDate char(10)

select @startDate = convert(char(10), dateadd(day, -3, getdate()), 101)
select @endDate = convert(char(10), getdate(), 101)

print ''
print 'Withdrawals Processed %1! - %2!', @startDate, @endDate
print ''

select substring(history,1,30) as "Old Symbol", 
substring(symbol,1,30) as "New Symbol", 
substring(markerName,1,50) as "New Name"
from MRK_History_View
where _Marker_Event_key in (2,3,4,5,6)
and event_date between @startDate and @endDate
order by symbol
go

