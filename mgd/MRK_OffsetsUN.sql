print ""
print "Markers with Offsets but no Chromosome Assignment"
print ""

select m._Marker_key, m.symbol from MRK_Marker m, MRK_Offset o
where m._Species_key = 1 and m.chromosome = 'UN' and m._Marker_key = o._Marker_key
and o.source = 0 and o.offset >= 0
union
select m._Marker_key, m.symbol from MRK_Marker m, MRK_Offset o
where m._Species_key = 1 and m.chromosome = 'UN' and m._Marker_key = o._Marker_key
and o.source = 1 and o.offset >= 0
order by m.symbol
go

