print ""
print "Mapped Markers w/out a Mapping Reference"
print "(excludes UN, MT, withdrawn markers, cytogenetic markers)"
print ""

select m._Marker_key, m.symbol, m.chromosome
from MRK_Marker m, MRK_Chromosome c
where m._Marker_Status_key = 1
and m._Species_key = 1
and m.chromosome not in ("MT", "UN")
and m._Marker_Type_key != 3
and not exists (select 1 from MLD_Marker e where m._Marker_key = e._Marker_key)
and not exists (select 1 from MLD_Expt_Marker e where m._Marker_key = e._Marker_key)
and m._Species_key = c._Species_key
and m.chromosome = c.chromosome
order by c.sequenceNum, m.symbol
go

