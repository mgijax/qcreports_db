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

create nonclustered index index_symbol on #markers(symbol)
go

select m.*, i.index_id
into #index
from #markers m, GXD_Index i
where i.comments like '% ' + m.symbol + ' %'
go

select m.*, a._Assay_key
into #assay
from #markers m, GXD_AssayNote a
where a.assayNote like '% ' + m.symbol + ' %'
go

select m.*, s._Assay_key
into #results
from #markers m, GXD_InSituResult n, GXD_Specimen s
where n.resultNote like '% ' + m.symbol + ' %'
and n._Specimen_key = s._Specimen_key
go

set nocount off
go

declare @month integer
declare @year integer
select @month = datepart(mm, getdate())
select @year = datepart(yy, getdate())

print ""
print "Symbols which have undergone withdrawals and appear in GXD Index Notes"
print "Nomenclature Event Date as of: %1!/%2!", @month, @year
print ""

select i.symbol "Marker Symbol", i.jnumID "J:",
convert(char(10), x.event_date, 101) "Event Date"
from #index x, GXD_Index_View i
where x.index_id = i.index_id
order by x.event_date desc
go

declare @month integer
declare @year integer
select @month = datepart(mm, getdate())
select @year = datepart(yy, getdate())

print ""
print "Symbols which have undergone withdrawals and appear in GXD Assay Notes"
print "Nomenclature Event Date: %1!/%2!", @month, @year
print ""

select x.symbol "Marker Symbol", a.mgiID "Assay MGI ID",
convert(char(10), x.event_date, 101) "Event Date"
from #assay x, GXD_Assay_View a
where x._Assay_key = a._Assay_key
order by x.event_date desc
go

declare @month integer
declare @year integer
select @month = datepart(mm, getdate())
select @year = datepart(yy, getdate())

print ""
print "Symbols which have undergone withdrawals and appear in GXD Result Notes"
print "Nomenclature Event Date: %1!/%2!", @month, @year
print ""

select x.symbol "Marker Symbol", a.mgiID "Assay MGI ID",
convert(char(10), x.event_date, 101) "Event Date"
from #results x, GXD_Assay_View a
where x._Assay_key = a._Assay_key
order by x.event_date desc
go

