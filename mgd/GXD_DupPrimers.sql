
/* TR 7454 */

set nocount on
go

/* all primers */

select _Probe_key, name = substring(name, 1, 50), 
primer1sequence = substring(primer1sequence, 1,50), 
primer2sequence = substring(primer2sequence, 1, 50)
into #primers
from PRB_Probe
where _SegmentType_key = 63473
go

create index idx1 on #primers(_Probe_key)
create index idx2 on #primers(primer1sequence)
create index idx3 on #primers(primer2sequence)
go

/* primers that are duplicates by sequence */

select p1.*, probeKey2 = p2._Probe_key, primer2 = p2.name
into #dups
from #primers p1, #primers p2
where p1.primer1sequence = p2.primer1sequence
and p1.primer2sequence = p2.primer2sequence
and p1._Probe_key != p2._Probe_key
go

/* duplicates that appear in GXD */

select distinct p.*
into #gxd
from #dups p, GXD_ProbePrep g
where p._Probe_key = g._Probe_key
or p.probeKey2 = g._Probe_key
go

set nocount off
go

print ""
print "Primer Sets whose Sequences are identical and one of the Primer Sets is used in a GXD Assay"
print ""

select accID1 = substring(a1.accID,1,15), primer1 = d.name, 
accID2 = substring(a2.accID,1,15), d.primer2, d.primer1sequence, d.primer2sequence
from #gxd d, ACC_Accession a1, ACC_Accession a2
where d._Probe_key = a1._Object_key
and a1._MGIType_key = 3
and a1._LogicalDB_key = 1
and a1.prefixPart = "MGI:"
and a1.preferred = 1
and d.probeKey2 = a2._Object_key
and a2._MGIType_key = 3
and a2._LogicalDB_key = 1
and a2.prefixPart = "MGI:"
and a2.preferred = 1
order by primer1
go

