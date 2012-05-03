set nocount on
go

select a._Assay_key, a._Marker_key, p._Probe_key
into #probe
from GXD_Assay a, GXD_ProbePrep p
where a._ProbePrep_key = p._ProbePrep_key
and a._AssayType_key in (1,2,3,4,5,6,8)
go

set nocount off
go

print ''
print 'GXD Assay Probe/Marker Pairs No Longer Found in Master Probe Table'
print ''

select a.accID as 'Assay', pb.name as 'Probe', m.symbol as 'Marker'
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
and a._AssayType_key in (1,2,3,4,5,6,8)
go

set nocount off
go

print ''
print 'GXD Assay Antibody/Marker Pairs No Longer Found in Master Antibody Table'
print ''

select m.symbol as 'Marker', substring(b.antibodyName,1,75) as 'Antibody', a.accID as 'Assay'
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
and a._AssayType_key in (1,2,3,4,5,6,8)
and not exists (select 1 from PRB_Reference r
		where p._Probe_key = r._Probe_key
                and a._Refs_key = r._Refs_key)
go

set nocount off
go

print ''
print 'GXD Assay Probes with no corresponding entry in the Probe Reference Table'
print ''

select a.accID as 'Assay', b.accID as 'J Number', pb.name as 'Probe'
from #proberef p, ACC_Accession a, ACC_Accession b, PRB_Probe pb
where p._Assay_key = a._Object_key
and a._MGIType_key = 8
and p._Refs_key = b._Object_key
and b._MGIType_key = 1
and b._LogicalDB_key = 1 
and b.prefixPart = 'J:'
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

print ''
print 'Dummy Sequence Records Annotated to GXD Mouse Molecular Segments'
print ''

select distinct ma.accID as 'MGI ID', substring(p.name,1,30) as 'Molecular Segment', 
sa.accID as 'Sequence', substring(l.name, 1, 25), u.login, d.annotation_date
from #probedummy2 d, PRB_Probe p, GXD_ProbePrep g, ACC_Accession ma, ACC_Accession sa, ACC_LogicalDB l, MGI_User u
where d._Probe_key = p._Probe_key
and d._Probe_key = g._Probe_key
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

select d.accID as seqID, pa2.accID as mgiID, substring(p.name,1,30) as name
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

print ''
print 'Deleted Sequences with GXD Associations'
print ''
print 'A row in this report represents a Sequence that is designated as Deleted'
print 'by the Sequence provider and contains associations to a GXD Molecular Segment.'
print ''

select seqID, mgiID, name from #pdeleted
go

set nocount on

select distinct pm._Probe_key, pm._Marker_key
into #encodes
from PRB_Marker pm, GXD_ProbePrep g
where g._Probe_key = pm._Probe_key
and pm.relationship = 'E'
go

select * into #multencodes from #encodes group by _Probe_key having count(*) > 1
go

create index idx1 on #multencodes(_Probe_key)
create index idx2 on #multencodes(_Marker_key)
go

set nocount off

print ''
print 'Probe w/ more than one encodes relationship'
print ''

select distinct a.accid, p.name, m.symbol
from #multencodes e, PRB_Probe p, MRK_Marker m, ACC_Accession a
where e._Probe_key = p._Probe_key
and e._Probe_key = a._Object_key
and a._MGIType_key = 3
and a._Logicaldb_key = 1
and a.prefixPart = 'MGI:'
and a.preferred = 1
and e._Marker_key = m._Marker_key
order by a.accid
go

print ''
print 'Antigens with source information but both tissue and cell line are Not specified'
print ''

set nocount on

select distinct _Antigen_key, antigenName, mgiID 
into #antigens 
from GXD_Antigen_View  g, PRB_Source s 
where s._Source_key = g._Source_key 
and g._Organism_key = 1  
and g._CellLine_key = 316335  
and g._Tissue_key = -1  
and s.description is not null
go

insert into #antigens 
select distinct _Antigen_key, antigenName, mgiID 
from GXD_Antigen_View 
where _Organism_key = 1
and _CellLine_key = 316335 
and _Tissue_key = -1 
and (age != 'Not Specified' 
or _Strain_key != -1 
or _Gender_key != 315167)
go

set nocount off

select mgiID, antigenName
from #antigens
go

print ''
print 'Mouse cDNAs with gene associations and source information but both tissue and cell line are Not specified'
print ''

set nocount on

select distinct m._Probe_key, m.name as cDNAname, p.mgiID 
into #probes 
from PRB_Source s, PRB_Probe_View p, PRB_Marker_View m
where s._Organism_key = 1 
and p._SegmentType_key = 63468 
and s._CellLine_key = 316335 
and s._Tissue_key = -1 
and s._Source_key = p._Source_key 
and p._Probe_key = m._Probe_key 
and (s.age != 'Not Specified' 
or s._Strain_key != -1 
or s._Gender_key != 315167)
go

insert into #probes 
select distinct m._Probe_key, m.name, p.mgiID 
from PRB_Source s, PRB_Probe_View p, PRB_Marker_View m
where s._Organism_key = 1 
and p._SegmentType_key = 63468 
and s._CellLine_key = 316335 
and s._Tissue_key = -1 
and s._Source_key = p._Source_key 
and p._Probe_key = m._Probe_key 
and s.description is not null
go

set nocount off

select mgiID, cDNAname
from #probes
go
