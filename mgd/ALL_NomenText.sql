set nocount on
go

select distinct h._History_key, h.event_date, r.symbol, r.current_symbol
into #markers
from MRK_History h, MRK_Current_View r
where datepart(mm, h.event_date) = datepart(mm, getdate())
and datepart(yy, h.event_date) = datepart(yy, getdate())
and h._Marker_Event_key in (2,3,4,5)
and h._History_key = r._Marker_key
go

set nocount off
go

declare @month integer
declare @year integer
select @month = datepart(mm, getdate())
select @year = datepart(yy, getdate())

print ""
print "Symbols which have undergone withdrawals and appear in Allele Molecular Notes"
print "Nomenclature Event Date: %1!/%2!", @month, @year
print ""

select a.symbol "Allele Symbol", m.symbol "Old Symbol", m.current_symbol "New Symbol", 
convert(char(10), m.event_date, 101) "Event Date"
from #markers m, ALL_Allele a, ALL_Note_Molecular_View n
where n.note like '% ' + m.symbol + ' %'
and n._Allele_key = a._Allele_key
order by m.event_date desc
go

