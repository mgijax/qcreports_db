print ""
print "Marker Aliases w/ Different Offsets"
print ""

select l1.symbol, l2.symbol "alias", str(lo1.offset,10,2) "symbol offset", str(lo2.offset,10,2) "alias offset"
from MRK_Marker l1, MRK_Marker l2, MRK_Alias la, MRK_Offset lo1, MRK_Offset lo2
where l1._Marker_key = la._Marker_key
and la._Alias_key = l2._Marker_key
and l1._Marker_key = lo1._Marker_key
and lo1.source = 0
and l2._Marker_key = lo2._Marker_key
and lo2.source = 0
and lo1.offset != lo2.offset
order by l1.symbol
go

print ""
print "Marker Aliases w/ Single Links"
print ""

select m1.symbol, m2.symbol "alias"
from MRK_Alias a, MRK_Marker m1, MRK_Marker m2
where not exists (select b.* from MRK_Alias b where a._Marker_key = b._Alias_key
and a._Alias_key = b._Marker_key)
and a._Marker_key = m1._Marker_key
and a._Alias_key = m2._Marker_key
order by m1.symbol
go

