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

