set nocount on
go

select h.symbol, h.history, h.event_date, h._Refs_key
into #alleles
from MRK_History_View h
where h._Marker_Event_key = 4
and datediff (month, h.event_date, getdate()) <= 2
and (
exists (select 1 from MLC_Text m where h._Marker_key = m._Marker_key)
or
exists (select 1 from MLC_Text m where h._History_key = m._Marker_key)
)
go

set nocount off
go

print ""
print "Allele Withdrawals in Last 2 Months where either Old or New Gene has MLC record"
print ""

select a.history "Old Marker", a.symbol "New Marker", b.accID "Withdrawal Reference", 
a.event_date "Date Withdrawn"
from #alleles a, BIB_Acc_View b
where a._Refs_key = b._Object_key
and b.prefixPart = "J:"
order by a.event_date desc
go
