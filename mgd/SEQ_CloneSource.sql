set nocount on
go

select p._Probe_key, p._Source_key, a2._Object_key, a2.accID
into #probes
from PRB_Probe p, ACC_Accession a1, ACC_Accession a2
where p._Source_key > -2
and p._Probe_key = a1._Object_key
and a1._MGIType_key = 3
and a1.accID = a2.accID
and a2._MGIType_key = 19
and a1._LogicalDB_key = a2._LogicalDB_key
go

create nonclustered index idx_skey on #probes(_Object_key)
go

select p.*
into #diffsource1
from #probes p
where not exists (select 1 from SEQ_Source_Assoc s
where p._Object_key = s._Sequence_key
and p._Source_key = s._Source_key)
go

create nonclustered index idx_skey on #diffsource1(_Source_key)
go

create nonclustered index idx_okey on #diffsource1(_Object_key)
go

set nocount off
go

print ""
print "    Sequences and their Molecular Segments Associated with Different Sources"
print ""
print "    A row in this report represents a Sequence whose corresponding Molecular Segment"
print "    has a different Molecular Source and at least one of the Molecular Sources"
print "    is a Named Molecular Source."
print ""

select d.accID, sequenceSource = substring(ps2.name,1,50), probeSource = substring(ps1.name,1,50)
from #diffsource1 d, PRB_Source ps1, SEQ_Source_Assoc sa, PRB_Source ps2
where d._Source_key = ps1._Source_key
and ps1.name is not null
and d._Object_key = sa._Sequence_key
and sa._Source_key = ps2._Source_key
union
select d.accID, sequenceSource = substring(ps2.name,1,50), probeSource = substring(ps1.name,1,50)
from #diffsource1 d, PRB_Source ps1, SEQ_Source_Assoc sa, PRB_Source ps2
where d._Source_key = ps1._Source_key
and ps2.name is not null
and d._Object_key = sa._Sequence_key
and sa._Source_key = ps2._Source_key
order by sequenceSource
go

