set nocount on
go

/* molecular segments annotated to sequences */

select s._Sequence_key, s._Probe_key, a.accID
into #probes1
from SEQ_Probe_Cache s, ACC_Accession a
where s._Sequence_key = a._Object_key
and a._MGIType_key = 19
and a.preferred = 1
go

create index idx1 on #probes1(_Probe_key)
go

/* with _Source_key != Not Specified

select a._Sequence_key, p._Source_key, a.accID
into #probes2
from #probes1 a, PRB_Probe p
where a._Probe_key = p._Probe_key
and p._Source_key > -2
go

create index idx1 on #probes2(_Sequence_key)
create index idx2 on #probes2(_Source_key)
go

drop table #probes1
go

/* select probes that have different sources than their sequences */

select p._Sequence_key, p._Source_key, p.accID
into #diffsource1
from #probes2 p
where not exists (select 1 from SEQ_Source_Assoc s
where p._Sequence_key = s._Sequence_key
and p._Source_key = s._Source_key)
go

create index idx1 on #diffsource1(_Sequence_key)
create index idx2 on #diffsource1(_Source_key)
go

select d.accID, sequenceSource = substring(ps2.name,1,50), probeSource = substring(ps1.name,1,50)
into #diffsource2
from #diffsource1 d, PRB_Source ps1, SEQ_Source_Assoc sa, PRB_Source ps2
where d._Source_key = ps1._Source_key
and ps1.name is not null
and d._Sequence_key = sa._Sequence_key
and sa._Source_key = ps2._Source_key
go

create index idx1 on #diffsource2(accID)
create index idx2 on #diffsource2(sequenceSource)
go

select d.accID, sequenceSource = substring(ps2.name,1,50), probeSource = substring(ps1.name,1,50)
into #diffsource3
from #diffsource1 d, PRB_Source ps1, SEQ_Source_Assoc sa, PRB_Source ps2
where d._Source_key = ps1._Source_key
and ps2.name is not null
and d._Sequence_key = sa._Sequence_key
and sa._Source_key = ps2._Source_key
go

create index idx1 on #diffsource3(accID)
create index idx2 on #diffsource3(sequenceSource)
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

select accID, sequenceSource, probeSource from #diffsource2
union
select accID, sequenceSource, probeSource from #diffsource3
order by sequenceSource
go

