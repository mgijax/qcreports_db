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

