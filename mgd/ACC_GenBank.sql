set nocount on
go

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

select a.accID
into #accs2
from ACC_Accession a, MRK_Marker m
where a._LogicalDB_key = 9
and a._MGIType_key = 2
and a._Object_key = m._Marker_key
and m._Organism_key = 1
go

create index idx1 on #accs2(accID)
go

select distinct accID into #maccs from #accs2
go

create index idx1 on #maccs(accID)
go

print ""
print "All GenBank IDs in MGI associated with a Molecular Segment or Mouse Gene"
print ""

select accID from #paccs
union
select accID from #maccs
order by accID
go

