declare @startDate char(10)
declare @endDate char(10)

select @startDate = convert(char(10), dateadd(day, -3, getdate()), 101)
select @endDate = convert(char(10), getdate(), 101)

print ""
print "Withdrawals Processed %1! - %2!", @startDate, @endDate
print ""

select substring(history,1,30) "Old Symbol", substring(symbol,1,30) "New Symbol", markerName "New Name"
from MRK_History_View
where _Marker_Event_key in (2,3,4,5)
and event_date between @startDate and @endDate
order by symbol
go

