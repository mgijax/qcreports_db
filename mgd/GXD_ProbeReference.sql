set nocount on
go

select a._Assay_key, a._Refs_key, p._Probe_key
into #probe
from GXD_Assay a, GXD_ProbePrep p
where a._ProbePrep_key = p._ProbePrep_key
and a._AssayType_key != 9
and not exists (select r.* from PRB_Reference r where
                p._Probe_key = r._Probe_key
                and a._Refs_key = r._Refs_key)
go

set nocount off
go

print ""
print "GXD Assay Probes with no corresponding entry in the Probe Reference Table"
print ""

select a.accID "Assay", b.accID "J Number", pb.name "Probe"
from #probe p, ACC_Accession a, ACC_Accession b, PRB_Probe pb
where 
p._Assay_key = a._Object_key and 
and a._MGIType_key = 8
p._Refs_key = b._Object_key and
and b._MGIType_key = 1
p._Probe_key = pb._Probe_key
order by pb.name, a.accID
go

