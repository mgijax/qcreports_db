
set nocount on
go

/* select all where the a secondary id is annotated */

select ma._Object_key, ma.accID, sequenceKey = sa._Object_key
into #markers1
from ACC_Accession sa, ACC_Accession ma
where sa._MGIType_key = 19
and sa.preferred = 0
and sa.accID = ma.accID
and ma._MGIType_key = 2
and ma._LogicalDB_key = sa._LogicalDB_key
go

create nonclustered index idx_mkey on #markers1(_Object_key)
create nonclustered index idx_skey on #markers1(sequenceKey)
go

/* select all where the primary is not annotated */

select m.*
into #markers
from #markers1 m
where not exists (select 1 from ACC_Accession ma, ACC_Accession sa
where m._Object_key = ma._Object_key
and ma._MGIType_key = 2
and m.sequenceKey = sa._Object_key
and sa._MGIType_key = 19
and ma.accID = sa.accID
and sa.preferred = 1)
go

create nonclustered index idx_mkey on #markers(_Object_key)
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

