
set nocount on
go

select spc._Sequence_key, spc._Probe_key, smc._Marker_key, pm._Refs_key
into #autoE1
from SEQ_Probe_Cache spc, SEQ_Marker_Cache smc, PRB_Marker pm  
where spc._Sequence_key = smc._Sequence_key 
and spc._Probe_key = pm._Probe_key 
and smc._Marker_key = pm._Marker_key 
and pm.relationship = 'H'
go

create index idx1 on #autoE1(_Probe_key)
create index idx2 on #autoE1(_Marker_key)
create index idx3 on #autoE1(_Refs_key)
create index idx4 on #autoE1(_Sequence_key)
go

select distinct c._Probe_key
into #excluded
from SEQ_Probe_Cache c, SEQ_Sequence s
where c._Sequence_key = s._Sequence_key
and s._SequenceQuality_key = 316340
go

create index idx1 on #excluded(_Probe_key)
go

delete #autoE1 where _Probe_key in (select _Probe_key from #excluded)
go

set nocount off
go

print ""
print "    Molecular Segments and Markers Eligible for Auto-E"
print ""
print "A row in this report represents a Molecular Segment/Marker pair that is"
print "eligible for an auto-E, but cannot participate in the auto-E load"
print "because it has a manually curated 'H' associations."
print ""

select seqID = sa.accID, jNum = b.accID, SegmentID = pa.accID, 
	SegmentName = p.name, MarkerID = ma.accID, markerSymbol = m.symbol
from #autoE1 s, ACC_Accession sa, ACC_Accession b, ACC_Accession ma,
MRK_Marker m, ACC_Accession pa, PRB_Probe p
where s._Sequence_key = sa._Object_key 
and sa._MGIType_key = 19
and sa.preferred = 1 
and sa._LogicalDB_key = 9
and s._Refs_key = b._Object_key 
and b._MGIType_key = 1
and b._LogicalDB_key = 1
and b.prefixPart = 'J:'
and b.preferred = 1
and s._Marker_key = m._Marker_key
and m._Marker_key = ma._Object_key
and ma._LogicalDB_key = 1
and ma._MGIType_key = 2
and ma.prefixPart = 'MGI:'
and ma.preferred = 1
and s._Probe_key = p._Probe_key
and p._Probe_key = pa._Object_key
and pa._MGIType_key = 3
and pa._LogicalDB_key = 1
and pa.prefixPart = 'MGI:'
and pa.preferred = 1
order by sa.accID
go

