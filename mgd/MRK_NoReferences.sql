print ""
print "Markers (excluding withdrawns) Without ANY References"
print ""

select distinct m._Marker_key, m.symbol
from MRK_Marker m
where m._Organism_key = 1
and m._Marker_Status_key in (1,3)
and not exists (select r.* from MRK_Reference r
where m._Marker_key = r._Marker_key)
and not exists (select r.* from MLC_Reference r
where m._Marker_key = r._Marker_key)
order by m.symbol
go

