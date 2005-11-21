set nocount on
go

select p._Probe_key, p.name, DNAtype = t.term, p._Source_key, p.modification_date
into #preprobe
from PRB_Probe p, VOC_Term t
where p._SegmentType_key = t._Term_key
and t.term != "primer"
and _Source_key != 30040
and name not like 'MGC clone%'
and name not like 'IMAGE clone%'
and name not like 'RPCI23 clone%'
and name not like 'RPCI24 clone%'
and name not like 'NIA clone%'
and name not like 'RIKEN clone%'
go

create index idx1 on #preprobe(_Probe_key)
go

select *
into #probe
from #preprobe
group by name
having count(*) > 1
go

create index idx1 on #probe(_Probe_key)
go

select m.symbol, p.name, p.DNAtype, organism = o.commonName, p.modification_date
into #markers
from #probe p, PRB_Marker pm, MRK_Marker m, PRB_Source s, MGI_Organism o
where p._Probe_key = pm._Probe_key
and pm._Marker_key = m._Marker_key
and p._Source_key = s._Source_key
and s._Organism_key = o._Organism_key
go

create index idx1 on #markers(name)
create index idx2 on #markers(symbol)
create index idx3 on #markers(modification_date)
go

set nocount off
go

print ""
print "Probes Names Used More Than Once for the Same Marker"
print ""

select name = substring(name,1,25), symbol, modification_date
from #markers
group by name, symbol, DNAtype, organism
having count(*) > 1
order by name, symbol, modification_date desc
go

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
go

create index idx1 on #probe(_Probe_key)
go

set nocount off
go

print ""
print "Probes - No Markers (excluding MGC, IMAGE, RPCI, NIA, RIKEN clones)"
print ""

select p.name, p.creation_date, p._Probe_key
from #probe p
where not exists (select m.* from PRB_Marker m where p._Probe_key = m._Probe_key)
order by p.creation_date, p.name
go

