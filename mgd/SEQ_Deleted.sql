
set nocount on
go

select s._Sequence_key
into #deleted1
from SEQ_Sequence s, VOC_Term t
where s._SequenceStatus_key = t._Term_key
and t.term = "DELETED"
go

select a.accID
into #deleted2
from #deleted1 d, SEQ_Sequence_Acc_View a
where d._Sequence_key = a._Object_key
go

set nocount off
go

print ""
print "Deleted Sequences with MGI Associations"
print ""

select seqID = d.accID, mgiID = ma.accID, name = m.symbol
from #deleted2 d, MRK_Acc_View ma, MRK_Marker m
where d.accID = ma.accID
and ma._Object_key = m._Marker_key
union
select d.accID, mgiID = pa.accID, p.name
from #deleted2 d, PRB_Acc_View pa, PRB_Probe p
where d.accID = pa.accID
and pa._Object_key = p._Probe_key
go

