set nocount on
go

/* select markers which contain references */
/* exclude withdrawns */

select distinct m._Marker_key, m.symbol
into #markers
from MRK_Marker m, MRK_Reference r
where m._Organism_key = 1
and m._Marker_Status_key in (1,3)
and m._Marker_key = r._Marker_key
union
select distinct m._Marker_key, m.symbol
from MRK_Marker m, MLC_Reference r
where m._Organism_key = 1
and m._Marker_Status_key in (1,3)
and m._Marker_key = r._Marker_key
go

set nocount off
go

print ""
print "Markers (excluding withdrawns) Without History References or History"
print ""

select distinct m.symbol
from #markers m, MRK_History h
where m._Marker_key = h._Marker_key
and h._Refs_key is null
union
select distinct m.symbol
from #markers m
where not exists (select * from MRK_History h
where m._Marker_key = h._Marker_key)
order by m.symbol
go

