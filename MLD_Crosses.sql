print ""
print "Mapping Panels Displayed in Lookup List"
print ""

select whoseCross "Mapping Panel", type "Cross Type", _Cross_key "Cross Key"
from CRS_Cross where displayed = 1
order by whoseCross
go

