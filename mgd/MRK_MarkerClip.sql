
print ""
print "Genes with Marker Clips and Alleles that have been added in the last 5 days"
print ""

select distinct m.symbol "Marker", a.symbol "Allele", a.creation_date "Allele Created", n.modification_date "Notes Modified"
from MRK_Marker m, ALL_Allele a, MRK_Notes n
where m._Marker_key = a._Marker_key
and m._Marker_key = n._Marker_key
and a.creation_date >= dateadd(day, -5, getdate())
order by m.symbol
go

