set nocount on
go

select distinct m._Expt_key, m._Marker_key 
into #expts
from MLD_Expt_Marker m, MLD_RIData d
where m._Expt_key = d._Expt_key
and not exists (select e.* from MLD_RIData e where 
m._Marker_key = e._Marker_key
and m._Expt_key = e._Expt_key)
union
select distinct m._Expt_key, m._Marker_key 
from MLD_Expt_Marker m, MLD_RI2Point d
where m._Expt_key = d._Expt_key
and not exists (select e.* from MLD_RI2Point e where 
m._Marker_key = e._Marker_key_1
and m._Expt_key = e._Expt_key)
union
select distinct m._Expt_key, m._Marker_key 
from MLD_Expt_Marker m, MLD_RI2Point d
where m._Expt_key = d._Expt_key
and not exists (select e.* from MLD_RI2Point e where 
m._Marker_key = e._Marker_key_2
and m._Expt_key = e._Expt_key)
union
select distinct m._Expt_key, m._Marker_key 
from MLD_Expt_Marker m, MLD_MC2point d
where m._Expt_key = d._Expt_key
and not exists (select e.* from MLD_MC2point e where 
m._Marker_key = e._Marker_key_1
and m._Expt_key = e._Expt_key)
union
select distinct m._Expt_key, m._Marker_key 
from MLD_Expt_Marker m, MLD_MC2point d
where m._Expt_key = d._Expt_key
and not exists (select e.* from MLD_MC2point e where 
m._Marker_key = e._Marker_key_2
and m._Expt_key = e._Expt_key)
go
 
delete #expts
from #expts e, MLD_RIData d
where e._Expt_key = d._Expt_key
and e._Marker_key = d._Marker_key
go

delete #expts
from #expts e, MLD_RI2Point d
where e._Expt_key = d._Expt_key
and e._Marker_key = d._Marker_key_1
go

delete #expts
from #expts e, MLD_RI2Point d
where e._Expt_key = d._Expt_key
and e._Marker_key = d._Marker_key_2
go

delete #expts
from #expts e, MLD_Matrix d
where e._Expt_key = d._Expt_key
go

delete #expts
from #expts e, MLD_MC2point d
where e._Expt_key = d._Expt_key
and e._Marker_key = d._Marker_key_1
go

delete #expts
from #expts e, MLD_MC2point d
where e._Expt_key = d._Expt_key
and e._Marker_key = d._Marker_key_2
go

set nocount off
go

print ""
print "Mapping - Markers in Experiment Marker List - Not Used in Experimental Data"
print ""

select distinct c.jnum, exptType = substring(x.exptType, 1, 30), x.tag, m.symbol
from #expts e, BIB_View c, MLD_Expts x, MLD_Expt_Marker em, MRK_Marker m
where e._Expt_key = x._Expt_key
and c._Refs_key = x._Refs_key
and x._Expt_key = em._Expt_key
and em._Marker_key = m._Marker_key
order by c.jnum, x.exptType, x.tag
go

set nocount on
go

drop table #expts
go

select distinct e = a._Expt_key, m = a._Marker_key_1
into #markers
from MLD_MC2point a
where not exists (select m.* from MLD_Expt_Marker m
where a._Expt_key = m._Expt_key
and a._Marker_key_1 = m._Marker_key)
union
select distinct e = a._Expt_key, m = a._Marker_key_2
from MLD_MC2point a
where not exists (select m.* from MLD_Expt_Marker m
where a._Expt_key = m._Expt_key
and a._Marker_key_2 = m._Marker_key)
go

set nocount off
go

print ""
print "Mapping - Markers in Experimental Data - Not in Experiment Marker List"
print ""

print ""
print "2x2 Cross"
print ""

select distinct exptType = substring(e.exptType, 1, 30), e.tag, m.symbol, b.jnum, substring(b.short_citation, 1, 30)
from #markers s, MLD_Expts e, BIB_View b, MRK_Marker m
where s.e = e._Expt_key
and e._Refs_key = b._Refs_key
and s.m = m._Marker_key
order by b.jnum, e.exptType, e.tag
go

set nocount on
go

drop table #markers
go

select distinct e = a._Expt_key, m = a._Marker_key_1
into #markers
from MLD_RI2point a
where not exists (select m.* from MLD_Expt_Marker m
where a._Expt_key = m._Expt_key
and a._Marker_key_1 = m._Marker_key)
union
select distinct e = a._Expt_key, m = a._Marker_key_2
from MLD_RI2point a
where not exists (select m.* from MLD_Expt_Marker m
where a._Expt_key = m._Expt_key
and a._Marker_key_2 = m._Marker_key)
go

set nocount off
go

print ""
print "2x2 RI"
print ""

select distinct exptType = substring(e.exptType, 1, 30), e.tag, m.symbol, b.jnum, substring(b.short_citation, 1, 30)
from #markers s, MLD_Expts e, BIB_View b, MRK_Marker m
where s.e = e._Expt_key
and e._Refs_key = b._Refs_key
and s.m = m._Marker_key
order by b.jnum, e.exptType, e.tag
go

set nocount on
go

drop table #markers
go

select distinct e = a._Expt_key, m = a._Marker_key
into #markers
from MLD_RIData a
where not exists (select m.* from MLD_Expt_Marker m
where a._Expt_key = m._Expt_key
and a._Marker_key = m._Marker_key)
go

set nocount off
go

print ""
print "RI Data"
print ""

select distinct exptType = substring(e.exptType, 1, 30), e.tag, m.symbol, b.jnum, substring(b.short_citation, 1, 30)
from #markers s, MLD_Expts e, BIB_View b, MRK_Marker m
where s.e = e._Expt_key
and e._Refs_key = b._Refs_key
and s.m = m._Marker_key
order by b.jnum, e.exptType, e.tag
go

set nocount on
go

drop table #markers
go

select distinct e = a._Expt_key, m = a._Marker_key_1
into #markers
from MLD_Distance a
where not exists (select m.* from MLD_Expt_Marker m
where a._Expt_key = m._Expt_key
and a._Marker_key_1 = m._Marker_key)
union
select distinct e = a._Expt_key, m = a._Marker_key_2
from MLD_Distance a
where not exists (select m.* from MLD_Expt_Marker m
where a._Expt_key = m._Expt_key
and a._Marker_key_2 = m._Marker_key)
go
 
set nocount off
go

print ""
print "Physical Mapping"
print ""
 
select distinct exptType = substring(e.exptType, 1, 30), e.tag, m.symbol, b.jnum, substring(b.short_citation, 1, 30)
from #markers s, MLD_Expts e, BIB_View b, MRK_Marker m
where s.e = e._Expt_key
and e._Refs_key = b._Refs_key
and s.m = m._Marker_key
order by b.jnum, e.exptType, e.tag
go
 
drop table #markers
go
 
