set nocount on
go

/* Only Markers w/ <= 2 Reference */

select distinct r._Marker_key, r._Refs_key
into #markers
from MLC_Reference r
group by r._Marker_key
having count(*) <= 2
go

/* History Incomplete */

select distinct r._Marker_key, r._Refs_key
into #markers2
from #markers r, MRK_History h
where r._Marker_key = h._Marker_key
and (h._Refs_key is null
or h.name is null
or h.event_date is null)
go

set nocount off
go

print ""
print "MLC Markers w/ <= 2 References"
print ""

select m.symbol, m.chromosome
from #markers2 r, MRK_Marker m
where r._Marker_key = m._Marker_key
order by m.chromosome, m.symbol
go

