print ""
print "Withdrawn Markers w/ MLC Text"
print ""

select m.symbol
from MLC_Text_edit c, MRK_Marker m
where c._Marker_key = m._Marker_key
and m._Marker_Status_key = 2
order by m.symbol
go
