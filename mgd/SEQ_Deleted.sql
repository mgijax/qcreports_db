
set nocount on
go

/* delete Sequences */

select s._Sequence_key
into #deleted1
from SEQ_Sequence s
where s._SequenceStatus_key = 316343
go

create index idx1 on #deleted1(_Sequence_key)
go

/* their accession ids (primary and secondary) */

select a.accID, d._Sequence_key
into #deleted2
from #deleted1 d, ACC_Accession a
where d._Sequence_key = a._Object_key
and a._MGIType_key = 19
go

create index idx1 on #deleted2(accID)
create index idx2 on #deleted2(_Sequence_key)
go

/* deleted sequences annotated to mouse markers */

select d.accID as seqID, ma2.accID as mgiID, m.symbol as name
into #mdeleted
from #deleted2 d, SEQ_Marker_Cache ma, ACC_Accession ma2, MRK_Marker m
where d._Sequence_key = ma._Sequence_key
and ma._Marker_key = ma2._Object_key 
and ma2._MGIType_key = 2
and ma2._LogicalDB_key = 1
and ma2.prefixPart = 'MGI:'
and ma2.preferred = 1
and ma._Marker_key = m._Marker_key 
go

create index idx1 on #mdeleted(seqID)
go

/* deleted sequences annotated to molecular segments */

select d.accID as seqID, pa2.accID as mgiID, p.name
into #pdeleted
from #deleted2 d, SEQ_Probe_Cache pa, ACC_Accession pa2, PRB_Probe p
where d._Sequence_key = pa._Sequence_key
and pa._Probe_key = pa2._Object_key
and pa2._MGIType_key = 3
and pa2._LogicalDB_key = 1
and pa2.prefixPart = 'MGI:'
and pa2.preferred = 1
and pa._Probe_key = p._Probe_key
go

create index idx1 on #pdeleted(seqID)
go

set nocount off
go

print ''
print '    Deleted Sequences with MGI Associations'
print ''
print 'A row in this report represents a Sequence that is designated as Deleted'
print 'by the Sequence provider and contains associations to Marker and/or Molecular Segment.'
print ''
print 'Includes: all marker statuses (interim, official, withdrawn)'
print 'Includes: all marker types (gene, DNA segment, etc.)'
print ''

select seqID, mgiID, name from #mdeleted
union
select seqID, mgiID, name from #pdeleted
go

drop table #deleted1
go
drop table #deleted2
go
drop table #mdeleted
go
drop table #pdeleted
go

