
set nocount on
go

select s._Sequence_key
into #split1
from SEQ_Sequence s, VOC_Term t
where s._SequenceStatus_key = t._Term_key
and t.term = "SPLIT"
go

select a.accID
into #split2
from #split1 s, SEQ_Sequence_Acc_View a
where s._Sequence_key = a._Object_key
and a.preferred = 1
go

set nocount off
go

print ""
print "Split Sequences"
print ""
print "A row in this report represents a Sequence that is designated as Split"
print "by the Sequence Provider."
print ""

select seqID = s.accID
from #split2 s
order by seqID
go

