
set nocount off
go

print ""
print "    Sequences Modified More Recently Than Marker Annotation"
print ""
print "A row in this report represents a Sequence whose Sequence Modification"
print "Date is later than the last time a Curator annotated the Sequence"
print "to a Marker."
print ""

select seqID = sa.accID
from SEQ_Sequence s, SEQ_Sequence_Acc_View sa
where s._Sequence_key = sa._Object_key
and sa.preferred = 1
and s.modification_date >
(select max(annotation_date) from SEQ_Marker_Cache smc
 where smc._Sequence_key = s._Sequence_key)
go

