set nocount on
go

select p._Probe_key, p.name, pm._Marker_key
into #clone1
from PRB_Probe p, PRB_Marker pm
where p._Probe_key = pm._Probe_key
and pm.relationship = "E"
and exists (select 1 from ACC_Accession a
where p._Probe_key = a._Object_key
and a._MGIType_key = 3
and a._LogicalDB_key = 17)
go

create index idx1 on #clone1(_Probe_key)
create index idx2 on #clone1(_Marker_key)
go

select c.*, caccID = pa.accID, maccID = ma.accID
into #clone2
from #clone1 c, ACC_Accession pa, ACC_Accession ma
where c._Probe_key = pa._Object_key
and pa._MGIType_key = 3
and pa.prefixPart = "MGI:"
and pa._LogicalDB_key = 1
and pa.preferred = 1
and c._Marker_key = ma._Object_key
and ma._MGIType_key = 2
and ma.prefixPart = "MGI:"
and ma._LogicalDB_key = 1
and ma.preferred = 1
go

create index idx1 on #clone2(_Probe_key)
create index idx2 on #clone2(_Marker_key)
go

select c.caccID, c.maccID, a.accID
into #clone3
from #clone2 c, ACC_Accession a
where c._Probe_key = a._Object_key
and a._MGIType_key = 3
and a._LogicalDB_key = 9
and not exists (select 1 from ACC_Accession ma
where c._Marker_key = ma._Object_key
and ma._MGIType_key = 2
and ma.accID = a.accID)
go

create index idx1 on #clone3(caccID)
create index idx2 on #clone3(maccID)
go

select c.maccID, c.caccID, a.accID
into #clone4
from #clone2 c, ACC_Accession a
where c._Marker_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_key = 9
and not exists (select 1 from ACC_Accession ma
where c._Probe_key = ma._Object_key
and ma._MGIType_key = 3
and ma.accID = a.accID)
go

create index idx1 on #clone4(caccID)
create index idx2 on #clone4(maccID)
go

set nocount off
go

print ""
print "IMAGE Clones with Seq IDs which do not exist for encoding Markers"
print ""

select distinct c.caccID "Clone", c.maccID "Marker", c.accID
from #clone3 c
order by c.caccID
go

print ""
print "Markers with Seq IDs which do not exist for Clones to which the Marker encodes"
print ""

select distinct c.maccID "Marker", c.caccID "Clone", c.accID
from #clone4 c
order by c.maccID
go

set nocount on
go

drop table #clone1
drop table #clone2
drop table #clone3
go

select p._Probe_key, p.name, pm._Marker_key
into #clone1
from PRB_Probe p, PRB_Marker pm
where p._Probe_key = pm._Probe_key
and pm.relationship != "E"
and exists (select 1 from ACC_Accession a
where p._Probe_key = a._Object_key
and a._MGIType_key = 3
and a._LogicalDB_key = 17)
go

create index idx1 on #clone1(_Probe_key)
create index idx2 on #clone1(_Marker_key)
go

select c.*, seqID = pa.accID
into #clone2
from #clone1 c, ACC_Accession pa, ACC_Accession ma
where c._Probe_key = pa._Object_key
and pa._MGIType_key = 3
and pa._LogicalDB_key = 9
and c._Marker_key = ma._Object_key
and ma._MGIType_key = 2
and ma._LogicalDB_key = 9
and pa.accID = ma.accID
go

create index idx1 on #clone2(_Probe_key)
create index idx2 on #clone2(_Marker_key)
go

select caccID = ca.accID, maccID = ma.accID, c.seqID
into #clone3
from #clone2 c, ACC_Accession ca, ACC_Accession ma
where c._Probe_key = ca._Object_key
and ca._MGIType_key = 3
and ca.prefixPart= "MGI:"
and ca._LogicalDB_key = 1
and ca.preferred = 1
and c._Marker_key = ma._Object_key
and ma._MGIType_key = 2
and ma.prefixPart= "MGI:"
and ma._LogicalDB_key = 1
and ma.preferred = 1
go

create index idx1 on #clone3(seqID)
go

set nocount off
go

print ""
print "IMAGE Clones with Seq IDs which exist for non-encoding Markers"
print ""

select distinct caccID "Clone", maccID "Marker", seqID
from #clone3
order by seqID
go

