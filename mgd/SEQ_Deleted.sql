
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
print "    Deleted Sequences with MGI Associations"
print ""
print "A row in this report represents a Sequence that is designated as Deleted"
print "by the Sequence provider but that cannot be deleted from MGI by the"
print "automated process because it contains associations to Marker and/or"
print "Molecular Segments."
print ""

select seqID = d.accID, mgiID = ma2.accID, name = m.symbol
from #deleted2 d, MRK_Acc_View ma, MRK_Acc_View ma2, MRK_Marker m
where d.accID = ma.accID
and ma._Object_key = m._Marker_key 
and m._Marker_key = ma2._Object_key 
and ma2.prefixPart = 'MGI:'
and ma2.accID != ma.accID
union
select d.accID, mgiID = pa2.accID, p.name
from #deleted2 d, PRB_Acc_View pa, PRB_Acc_View pa2, PRB_Probe p
where d.accID = pa.accID
and pa._Object_key = p._Probe_key
and p._Probe_key = pa2._Object_key
and pa2.prefixPart = 'MGI:'
and pa2.accID != pa.accID
go

