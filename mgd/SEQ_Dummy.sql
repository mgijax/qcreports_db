set nocount on
go

select c._Marker_key, c.accID, c._LogicalDB_key, s._Sequence_key, c._CreatedBy_key, c.annotation_date
into #markerdummy
from SEQ_Marker_Cache c, SEQ_Sequence s
where c._Organism_key = 1
and c._Sequence_key = s._Sequence_key
and s._SequenceStatus_key = 316345
go

create index idx1 on #markerdummy(_Marker_key)
create index idx2 on #markerdummy(_Sequence_key)
create index idx3 on #markerdummy(_CreatedBy_key)
create index idx4 on #markerdummy(_LogicalDB_key)
go

select c._Probe_key, s._Sequence_key, c._CreatedBy_key, c.annotation_date
into #probedummy
from SEQ_Probe_Cache c, SEQ_Sequence s
where c._Sequence_key = s._Sequence_key
and s._SequenceStatus_key = 316345
go

create index idx1 on #probedummy(_Probe_key)
create index idx2 on #probedummy(_Sequence_key)
create index idx3 on #probedummy(_CreatedBy_key)
go

set nocount off
go

print ""
print "Dummy Sequence Records Annotated to Mouse Markers"
print ""
print "Includes: all marker statuses (interim, official, withdrawn)"
print "Includes: all marker types (gene, DNA segment, etc.)"
print ""

select ma.accID "MGI ID", substring(m.symbol,1,30) "Marker", 
d.accID "Sequence", substring(l.name, 1, 25) "LogicalDB Name", u.login, d.annotation_date
from #markerdummy d, MRK_Marker m, ACC_Accession ma, ACC_LogicalDB l, MGI_User u
where d._Marker_key = m._Marker_key
and d._Marker_key = ma._Object_key
and ma._MGIType_key = 2
and ma._LogicalDB_key = 1
and ma.prefixPart = "MGI:"
and ma.preferred = 1
and d._LogicalDB_key = l._LogicalDB_key
and d._CreatedBy_key = u._User_key
order by l.name, d.annotation_date, m.symbol
go

print ""
print "Dummy Sequence Records Annotated to Mouse Molecular Segments"
print ""
print "Includes: all marker statuses (interim, official, withdrawn)
print "Includes: all marker types (gene, DNA segment, etc.)
print ""

select ma.accID "MGI ID", substring(p.name,1,30) "Molecular Segment", 
sa.accID "Sequence", substring(l.name, 1, 25) "LogicalDB Name", u.login, d.annotation_date
from #probedummy d, PRB_Probe p, ACC_Accession ma, ACC_Accession sa, ACC_LogicalDB l, MGI_User u
where d._Probe_key = p._Probe_key
and d._Probe_key = ma._Object_key
and ma._MGIType_key = 3
and ma._LogicalDB_key = 1
and ma.prefixPart = "MGI:"
and ma.preferred = 1
and d._Sequence_key = sa._Object_key
and sa._MGIType_key = 19
and sa.preferred = 1
and sa._LogicalDB_key = l._LogicalDB_key
and d._CreatedBy_key = u._User_key
order by l.name, d.annotation_date, p.name
go

