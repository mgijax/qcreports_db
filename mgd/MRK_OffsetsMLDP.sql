set nocount on
go

select distinct m.symbol, m.chromosome, mo.offset, e.exptType,
modDate = convert(char(10), e.modification_date, 101), e._Refs_key
into #markers
from MRK_Marker m, MRK_Offset mo, MLD_Expt_Marker g, MLD_Expts e
where m._Organism_key = 1
and m._Marker_Status_key in (1,3)
and m._Marker_key = mo._Marker_key
and mo.source = 0
and mo.offset < 0
and m._Marker_key = g._Marker_key
and g._Expt_key = e._Expt_key
and e.modification_date >= dateadd(day, -3, getdate())
go

set nocount off
go

print ""
print "Markers with No Offsets Modifed in Mapping w/in the last 3 days"
print ""

select m.symbol, m.chromosome, m.offset, r.jnum, exptType = substring(m.exptType, 1, 30), m.modDate
from #markers m, BIB_All_View r
where m._Refs_key = r._Refs_key
order by m.chromosome, m.symbol, r.jnum
go

set nocount on
go

drop table #markers
go

select *
into #mgd
from MRK_Offset 
group by _Marker_key having count(*) = 1
go

delete from #mgd where source > 0
go

select distinct m.symbol, m.chromosome, d.offset, e.exptType,
modDate = convert(char(10), e.modification_date, 101), e._Refs_key
into #markers
from #mgd d, MRK_Marker m, MLD_Expt_Marker g, MLD_Expts e
where d._Marker_key = m._Marker_key
and m._Marker_key = g._Marker_key
and g._Expt_key = e._Expt_key
and e.modification_date >= dateadd(day, -3, getdate())
go
 
set nocount off
go

print ""
print "Markers with only MGD Offsets Modifed in Mapping w/in the last 3 days"
print ""
 
select m.symbol, m.chromosome, m.offset, r.jnum, exptType = substring(m.exptType, 1, 30), m.modDate
from #markers m, BIB_All_View r
where m._Refs_key = r._Refs_key
order by m.chromosome, m.symbol, r.jnum
go
 
set nocount on
go

drop table #markers
go

drop table #mgd
go

select *
into #mgd
from MRK_Offset o
where o.source = 0
and not exists (select o2.* from MRK_Offset o2
where o._Marker_key = o2._Marker_key
and o2.source = 1)
union
select o.*
from MRK_Offset o, MRK_Offset o2
where o._Marker_key = o2._Marker_key
and o2.source = 1
and o2.offset < 0
go

select distinct m.symbol, m.chromosome, d.offset, e.exptType,
modDate = convert(char(10), e.modification_date, 101), e._Refs_key
into #markers
from #mgd d, MRK_Marker m, MLD_Expt_Marker g, MLD_Expts e
where d._Marker_key = m._Marker_key
and m._Marker_key = g._Marker_key
and g._Expt_key = e._Expt_key
and e.modification_date >= dateadd(day, -3, getdate())
go
 
set nocount off
go

print ""
print "Markers with an MGD Offset but no CC Offset Modifed in Mapping w/in the last 3 days"
print ""
 
select m.symbol, m.chromosome, m.offset, r.jnum, exptType = substring(m.exptType, 1, 30), m.modDate
from #markers m, BIB_All_View r
where m._Refs_key = r._Refs_key
order by m.chromosome, m.symbol, r.jnum
go
 
