set nocount on
go

declare @processDate varchar(10)

select @processDate = convert(char(10), dateadd(day, -4, getdate()), 101)

print ""
print "Withdrawals Processed %1!", @processDate
print ""

select symbol "New Symbol", name "New Name", history "Old Symbol"
from MRK_History_View
where _Marker_Event_key = 2
and convert(char(10), event_date, 101) = @processDate
order by symbol
go

set nocount off
go

