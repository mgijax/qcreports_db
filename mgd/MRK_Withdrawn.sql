set nocount on
go

declare @startDate char(10)
declare @endDate char(10)

select @startDate = convert(char(10), dateadd(day, -3, getdate()), 101)
select @endDate = convert(char(10), getdate(), 101)

print ""
print "Withdrawals Processed %1! - %2!", @startDate, @endDate
print ""

select history "Old Symbol", symbol "New Symbol", markerName "New Name"
from MRK_History_View
where _Marker_Event_key = 2
and event_date between @startDate and @endDate
order by symbol
go

set nocount off
go

