
set nocount on
go

select s._Sequence_key
into #deleted1
from SEQ_Sequence s
where s._SequenceStatus_key = 316343
go

create index idx1 on #deleted1(_Sequence_key)
go

select a.accID, a._LogicalDB_key
into #deleted2
from #deleted1 d, ACC_Accession a
where d._Sequence_key = a._Object_key
and a._MGIType_key = 19
go

create index idx1 on #deleted2(accID)
create index idx2 on #deleted2(_LogicalDB_key)
go

select seqID = d.accID, mgiID = ma2.accID, name = m.symbol
into #mdeleted
from #deleted2 d, ACC_Accession ma, ACC_Accession ma2, MRK_Marker m
where d.accID = ma.accID
and d._LogicalDB_key = ma._LogicalDB_key
and ma._MGIType_key = 2
and ma._Object_key = ma2._Object_key 
and ma2._MGIType_key = 2
and ma2._LogicalDB_key = 1
and ma2.prefixPart = 'MGI:'
and ma2.preferred = 1
and ma._Object_key = m._Marker_key 
go

create index idx1 on #mdeleted(seqID)
go

select seqID = d.accID, mgiID = pa2.accID, p.name
into #pdeleted
from #deleted2 d, ACC_Accession pa, ACC_Accession pa2, PRB_Probe p
where d.accID = pa.accID
and d._LogicalDB_key = pa._LogicalDB_key
and pa._MGIType_key = 3
and pa._Object_key = pa2._Object_key
and pa2._MGIType_key = 3
and pa2._LogicalDB_key = 1
and pa2.prefixPart = 'MGI:'
and pa2.preferred = 1
and pa._Object_key = p._Probe_key
go

create index idx1 on #pdeleted(seqID)
go

set nocount off
go

print ""
print "    Deleted Sequences with MGI Associations"
print ""
print "A row in this report represents a Sequence that is designated as Deleted"
print "by the Sequence provider and contains associations to Marker and/or Molecular Segment."
print ""

select seqID, mgiID, name from #mdeleted
union
select seqID, mgiID, name from #pdeleted
go

