set nocount on
go

select c._Marker_key, s._Sequence_key
into #markerdummy
from SEQ_Marker_Cache c, SEQ_Sequence s
where c._Sequence_key = s._Sequence_key
and s._SequenceStatus_key = 316345
go

create index idx1 on #markerdummy(_Marker_key)
create index idx2 on #markerdummy(_Sequence_key)
go

select c._Probe_key, s._Sequence_key
into #probedummy
from SEQ_Probe_Cache c, SEQ_Sequence s
where c._Sequence_key = s._Sequence_key
and s._SequenceStatus_key = 316345
go

create index idx1 on #probedummy(_Probe_key)
create index idx2 on #probedummy(_Sequence_key)
go

set count on
go

print ""
print "Dummy Sequence Records Annotated to Mouse Markers"
print ""

select ma.accID "Marker", sa.accID "Sequence", substring(l.name, 1, 25)
from #markerdummy d, ACC_Accession ma, ACC_Accession sa, ACC_LogicalDB l
where d._Marker_key = ma._Object_key
and ma._MGIType_key = 2
and ma._LogicalDB_key = 1
and ma.prefixPart = "MGI:"
and ma.preferred = 1
and d._Sequence_key = sa._Object_key
and sa._MGIType_key = 19
and sa.preferred = 1
and sa._LogicalDB_key = l._LogicalDB_key
order by l.name, ma.accID
go

print ""
print "Dummy Sequence Records Annotated to Mouse Molecular Segments"
print ""

select ma.accID "Molecular Segment", sa.accID "Sequence", substring(l.name, 1, 25)
from #probedummy d, ACC_Accession ma, ACC_Accession sa, ACC_LogicalDB l
where d._Probe_key = ma._Object_key
and ma._MGIType_key = 3
and ma._LogicalDB_key = 1
and ma.prefixPart = "MGI:"
and ma.preferred = 1
and d._Sequence_key = sa._Object_key
and sa._MGIType_key = 19
and sa.preferred = 1
and sa._LogicalDB_key = l._LogicalDB_key
order by l.name, ma.accID
go

