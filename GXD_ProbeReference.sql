set nocount on
go

select a._Assay_key, a._Refs_key, p._Probe_key
into #probe
from GXD_Assay a, GXD_ProbePrep p
where a._ProbePrep_key = p._ProbePrep_key
and not exists (select r.* from PRB_Reference r where
                p._Probe_key = r._Probe_key
                and a._Refs_key = r._Refs_key)
go

set nocount off
go

print ""
print "GXD Assay Probes with no corresponding entry in the Probe Reference Table"
print ""

select a.accID "Assay", b.jnumID "J Number", pb.name "Probe"
from #probe p, GXD_Assay_Acc_View a, BIB_All_View b, PRB_Probe pb
where 
p._Assay_key = a._Object_key and 
p._Refs_key = b._Refs_key and
p._Probe_key = pb._Probe_key
order by pb.name, a.accID
go

