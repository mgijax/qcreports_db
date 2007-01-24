set nocount on
go

select s._Sequence_key
into #sequence
from SEQ_Sequence s
where s._SequenceProvider_key = 316372
and s._SequenceStatus_key = 316342
and not exists (select 1 from SEQ_Marker_Cache m where s._Sequence_key = m._Sequence_key)
go

create index idx1 on #sequence(_Sequence_key)
go

set nocount off
go

print ""
print "NM Sequences that are not associated with a MGI Marker"
print ""

select a.accID
from #sequence s, ACC_Accession a
where s._Sequence_key = a._Object_key
and a._MGIType_key = 19
and a.prefixPart = 'NM_'
order by a.accID
go
