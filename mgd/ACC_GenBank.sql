set nocount on
go

/* GenBank IDs annotated to Molecular Segments */

select a.accID
into #accs1
from ACC_Accession a
where a._LogicalDB_key = 9
and a._MGIType_key = 3
go

create index idx1 on #accs1(accID)
go

select distinct accID into #paccs from #accs1
go

create index idx1 on #paccs(accID)
go

/* GenBank IDs annotated to Mouse Genes */

select c._Sequence_key
into #accs2
from SEQ_Marker_Cache c, VOC_Term t
where c._SequenceProvider_key = t._Term_key
and t.term like 'Genbank%'
go

create index idx1 on #accs2(_Sequence_key)
go

select distinct _Sequence_key into #accs3 from #accs2
go

create index idx1 on #accs3(_Sequence_key)
go

select a.accID
into #maccs
from #accs3 a2, ACC_Accession a
where a2._Sequence_key = a._Object_key
and a._MGIType_key = 19
go

create index idx1 on #maccs(accID)
go

set nocount off
go

print ""
print "All GenBank IDs in MGI associated with a Molecular Segment or Mouse Gene"
print ""

select accID from #paccs
union
select accID from #maccs
order by accID
go

