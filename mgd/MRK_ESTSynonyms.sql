
print ""
print "EST IDs and Gm Markers as Synonyms"
print ""

select m.symbol, o.name "synonym"
from MRK_Marker m, MRK_Other o
where m._Marker_key = o._Marker_key
and (o.name like "[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]"
or o.name like "Gm%")
order by m.symbol
go

