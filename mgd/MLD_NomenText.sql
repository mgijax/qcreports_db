set nocount on
go

select h._History_key, h.event_date, e._Expt_key, e._Refs_key, e.exptTYpe, e.tag
into #m1
from MRK_History h, MLD_Expt_Marker em, MLD_Expts e
where datepart(mm, h.event_date) = datepart(mm, getdate())
and datepart(yy, h.event_date) = datepart(yy, getdate())
and h._Marker_Event_key in (2,3,4,5)
and h._Marker_key = em._Marker_key
and em._Expt_key = e._Expt_key
and e.exptType like 'TEXT%'
go

declare @month integer
declare @year integer
select @month = datepart(mm, getdate())
select @year = datepart(yy, getdate())

set nocount off
go

print ""
print "Symbols which have undergone withdrawals and appear in Text Experiments"
print "Nomenclature Event Date: %1!/%2!", @month, @year
print ""

select r.symbol "old symbol", r.current_symbol "new symbol", convert(char(10), m.event_date, 101) "event date", 
b.jnum "J:", 
substring(m.exptType + convert(char(5), m.tag), 1, 30) "Expt Type", 
a.accID "Expt MGI #"
from #m1 m, MRK_Current_View r, BIB_All_View b, ACC_Accession a
where m._History_key = r._Marker_key 
and m._Refs_key = b._Refs_key 
and m._Expt_key = a._Object_key
and a._MGIType_key = 4
and a.prefixPart= "MGI:"
order by m.event_date desc
go

