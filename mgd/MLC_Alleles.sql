print ""
print "MLC Symbols which contain Alleles"
print ""

select m.symbol, m._Marker_key
from MLC_Text c, MRK_Marker m
where c._Marker_key = m._Marker_key
and c.description like '%<SUP>%</SUP>%'
order by m.symbol
go

