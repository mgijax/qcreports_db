select c._Marker_key, c.accID, c._LogicalDB_key, s._Sequence_key, c._CreatedBy_key, c.annotation_date
into #markerdummy
from SEQ_Marker_Cache c, SEQ_Sequence s
where c._Organism_key = 1
and c._Sequence_key = s._Sequence_key
and s._SequenceStatus_key = 316345
go

create index markerdummy_idx1 on #markerdummy(_Marker_key)
go
create index markerdummy_idx2 on #markerdummy(_Sequence_key)
go
create index markerdummy_idx3 on #markerdummy(_CreatedBy_key)
go
create index markerdummy_idx4 on #markerdummy(_LogicalDB_key)
go

select c._Probe_key, s._Sequence_key, c._CreatedBy_key, c.annotation_date
into #probedummy
from SEQ_Probe_Cache c, SEQ_Sequence s
where c._Sequence_key = s._Sequence_key
and s._SequenceStatus_key = 316345
go

create index probedummy_idx1 on #probedummy(_Probe_key)
go
create index probedummy_idx2 on #probedummy(_Sequence_key)
go
create index probedummy_idx3 on #probedummy(_CreatedBy_key)
go

\echo ''
\echo 'Dummy Sequence Records Annotated to Mouse Markers'
\echo ''
\echo 'Includes: all marker statuses (interim, official, withdrawn)'
\echo 'Includes: all marker types (gene, DNA segment, etc.)'
\echo ''

select ma.accID as "MGI ID", substring(m.symbol,1,30) as "Marker", 
d.accID as "Sequence", substring(l.name, 1, 25) as "LogicalDB Name", u.login, d.annotation_date
from #markerdummy d, MRK_Marker m, ACC_Accession ma, ACC_LogicalDB l, MGI_User u
where d._Marker_key = m._Marker_key
and d._Marker_key = ma._Object_key
and ma._MGIType_key = 2
and ma._LogicalDB_key = 1
and ma.prefixPart = 'MGI:'
and ma.preferred = 1
and d._LogicalDB_key = l._LogicalDB_key
and d._CreatedBy_key = u._User_key
order by l.name, d.annotation_date, m.symbol
go

\echo ''
\echo 'Dummy Sequence Records Annotated to Mouse Molecular Segments'
\echo ''
\echo 'Includes: all marker statuses (interim, official, withdrawn)'
\echo 'Includes: all marker types (gene, DNA segment, etc.)'
\echo ''

select ma.accID as "MGI ID", substring(p.name,1,30) as "Molecular Segment", 
sa.accID as "Sequence", substring(l.name, 1, 25) as "LogicalDB Name", u.login, d.annotation_date
from #probedummy d, PRB_Probe p, ACC_Accession ma, ACC_Accession sa, ACC_LogicalDB l, MGI_User u
where d._Probe_key = p._Probe_key
and d._Probe_key = ma._Object_key
and ma._MGIType_key = 3
and ma._LogicalDB_key = 1
and ma.prefixPart = 'MGI:'
and ma.preferred = 1
and d._Sequence_key = sa._Object_key
and sa._MGIType_key = 19
and sa.preferred = 1
and sa._LogicalDB_key = l._LogicalDB_key
and d._CreatedBy_key = u._User_key
order by l.name, d.annotation_date, p.name
go

