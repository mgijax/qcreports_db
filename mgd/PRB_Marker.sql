set nocount on
go

drop table #probe
go

select _Probe_key, _Marker_key
into #probe 
from PRB_Marker 
group by _Probe_key, _Marker_key 
having count(*) > 1
go

create index idx1 on #probe(_Probe_key)
create index idx2 on #probe(_Marker_key)
go

set nocount off
go

print ""
print "Probes - Duplicate Marker Symbols - Probably Due to Withdrawal of Symbol"
print ""

select p.name, m1.symbol
from #probe m, PRB_Probe p, MRK_Marker m1
where m._Probe_key = p._Probe_key
and m._Marker_key = m1._Marker_key
order by p.name
go

set nocount on
go

drop table #probe
go

select p.name, p.creation_date, p._Probe_key
into #probe
from PRB_Probe p, VOC_Term t
where p._SegmentType_key = t._Term_key
and t.term != "primer"
and p._Source_key != 30040
and p.name not like 'MGC clone%'
and p.name not like 'IMAGE clone%'
and p.name not like 'RPCI23 clone%'
and p.name not like 'RPCI24 clone%'
and p.name not like 'NIA clone%'
and p.name not like 'RIKEN clone%'
and p.name not like 'J%'
and datepart(year, p.creation_date) >= 2002
go

create index idx1 on #probe(_Probe_key)
go

set nocount off
go

print ""
print "Probes - No Markers (excluding MGC, IMAGE, RPCI, NIA, RIKEN clones)"
print "where probe record was created in 2002 or later"
print ""

select p.name, p.creation_date, p._Probe_key
from #probe p
where not exists (select m.* from PRB_Marker m where p._Probe_key = m._Probe_key)
order by p.creation_date, p.name
go

