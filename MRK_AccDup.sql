set nocount on
go

select accID, _Object_key, LogicalDB = substring(l.name, 1, 50)
into #acc
from ACC_Accession a, ACC_LogicalDB l
where a._MGIType_key = 2
and a._LogicalDB_Key in (9, 13)
and a._LogicalDB_key = l._LogicalDB_key
go

select *
into #accDups
from #acc
group by accID, LogicalDB having count(*) > 1
go

set nocount off
go

print ""
print "Duplicate Marker Accession Numbers (Sequence, SWISS-PROT)"
print ""

select a.accID, m.symbol, a.LogicalDB
from #accDups a, MRK_Marker m
where a._Object_key = m._Marker_key
order by a.LogicalDB, a.accID, m.symbol
go

