
set nocount on
go

select ma._Object_key, ma.accID
into #markers
from ACC_Accession ma, ACC_Accession sa
where ma._MGIType_key = 2
and ma.accID = sa.accID
and sa._MGIType_key = 19
and ma._LogicalDB_key = sa._LogicalDB_key
and sa.preferred = 0
go

create nonclustered index idx_key on #markers(_Object_key)
go

set nocount off
go

print ""
print "Markers Annotated to a Secondary Sequence Accession ID"
print ""

select distinct m.symbol, ma.accID
from #markers ma, MRK_Marker m
where ma._Object_key = m._Marker_key
order by m.symbol
go

