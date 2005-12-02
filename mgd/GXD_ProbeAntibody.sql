set nocount on
go

select a._Assay_key, a._Marker_key, p._Probe_key
into #probe
from GXD_Assay a, GXD_ProbePrep p
where a._ProbePrep_key = p._ProbePrep_key
and a._AssayType_key != 9
go

set nocount off
go

print ""
print "GXD Assay Probe/Marker Pairs No Longer Found in Master Probe Table"
print ""

select a.accID "Assay", pb.name "Probe", m.symbol "Marker"
from #probe p, PRB_Probe pb, MRK_Marker m, ACC_Accession a
where p._Probe_key = pb._Probe_key
and p._Marker_key = m._Marker_key
and p._Assay_key = a._Object_key
and a._MGIType_key = 8
and not exists (select 1 from PRB_Marker pm
                where p._Probe_key = pm._Probe_key
                and p._Marker_key = pm._Marker_key)
go

set nocount on
go

select a._Assay_key, a._Marker_key, p._Antibody_key
into #antibody
from GXD_Assay a, GXD_AntibodyPrep p
where a._AntibodyPrep_key = p._AntibodyPrep_key
and a._AssayType_key != 9
go

set nocount off
go

print ""
print "GXD Assay Antibody/Marker Pairs No Longer Found in Master Antibody Table"
print ""

select m.symbol "Marker", substring(b.antibodyName,1,75) "Antibody", a.accID "Assay"
from #antibody p, GXD_Antibody b, MRK_Marker m, ACC_Accession a
where p._Antibody_key = b._Antibody_key
and p._Marker_key = m._Marker_key
and p._Assay_key = a._Object_key
and a._MGIType_key = 8
and not exists (select 1 from GXD_AntibodyMarker bm
                where p._Antibody_key = bm._Antibody_key
                and p._Marker_key = bm._Marker_key)
go

set nocount on
go

select a._Assay_key, a._Refs_key, p._Probe_key
into #proberef
from GXD_Assay a, GXD_ProbePrep p
where a._ProbePrep_key = p._ProbePrep_key
and a._AssayType_key != 9
and not exists (select 1 from PRB_Reference r
		where p._Probe_key = r._Probe_key
                and a._Refs_key = r._Refs_key)
go

set nocount off
go

print ""
print "GXD Assay Probes with no corresponding entry in the Probe Reference Table"
print ""

select a.accID "Assay", b.accID "J Number", pb.name "Probe"
from #proberef p, ACC_Accession a, ACC_Accession b, PRB_Probe pb
where p._Assay_key = a._Object_key
and a._MGIType_key = 8
and p._Refs_key = b._Object_key
and b._MGIType_key = 1
and p._Probe_key = pb._Probe_key
order by pb.name, a.accID
go

set nocount on
go

select distinct c._Probe_key, s._Sequence_key, c._CreatedBy_key, c.annotation_date
into #probedummy
from SEQ_Probe_Cache c, SEQ_Sequence s
where c._Sequence_key = s._Sequence_key
and s._SequenceStatus_key = 316345
go

create index idx1 on #probedummy(_Probe_key)
create index idx2 on #probedummy(_Sequence_key)
create index idx3 on #probedummy(_CreatedBy_key)
go

select p.*
into #probedummy2
from #probedummy p, PRB_Probe pp, PRB_Source s
where p._Probe_key = pp._Probe_key
and pp._Source_key = s._Source_key
and s._Organism_key = 1
go

create index idx1 on #probedummy2(_Probe_key)
create index idx2 on #probedummy2(_Sequence_key)
create index idx3 on #probedummy2(_CreatedBy_key)
go

set nocount off
go

print ""
print "Dummy Sequence Records Annotated to GXD Mouse Molecular Segments"
print ""

select distinct ma.accID "MGI ID", substring(p.name,1,30) "Molecular Segment", 
sa.accID "Sequence", substring(l.name, 1, 25), u.login, d.annotation_date
from #probedummy2 d, PRB_Probe p, GXD_ProbePrep g, ACC_Accession ma, ACC_Accession sa, ACC_LogicalDB l, MGI_User u
where d._Probe_key = p._Probe_key
and d._Probe_key = g._Probe_key
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

set nocount on
go

select s._Sequence_key
into #deleted1
from SEQ_Sequence s
where s._SequenceStatus_key = 316343
go

create index idx1 on #deleted1(_Sequence_key)
go

select a.accID, d._Sequence_key
into #deleted2
from #deleted1 d, ACC_Accession a
where d._Sequence_key = a._Object_key
and a._MGIType_key = 19
go

create index idx1 on #deleted2(accID)
create index idx2 on #deleted2(_Sequence_key)
go

select seqID = d.accID, mgiID = pa2.accID, name = substring(p.name,1,30)
into #pdeleted
from #deleted2 d, SEQ_Probe_Cache pa, ACC_Accession pa2, PRB_Probe p, GXD_ProbePrep g
where d._Sequence_key = pa._Sequence_key
and pa._Probe_key = pa2._Object_key
and pa2._MGIType_key = 3
and pa2._LogicalDB_key = 1
and pa2.prefixPart = 'MGI:'
and pa2.preferred = 1
and pa._Probe_key = p._Probe_key
and pa._Probe_key = g._Probe_key
go

create index idx1 on #pdeleted(seqID)
go

set nocount off
go

print ""
print "Deleted Sequences with GXD Associations"
print ""
print "A row in this report represents a Sequence that is designated as Deleted"
print "by the Sequence provider and contains associations to a GXD Molecular Segment."
print ""

select seqID, mgiID, name from #pdeleted
go

