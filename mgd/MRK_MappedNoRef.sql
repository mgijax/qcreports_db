set nocount on
go

select m._Marker_key
into #markers
from MRK_Marker m
where m._Marker_Status_key in (1,3)
and m._Organism_key = 1
and m.chromosome not in ("MT", "UN")
and m._Marker_Type_key != 3
and not exists (select 1 from MLD_Marker e where m._Marker_key = e._Marker_key)
and not exists (select 1 from MLD_Expt_Marker e where m._Marker_key = e._Marker_key)
go

select distinct m._Marker_key
into #exclude
from #markers m, MRK_Reference r
where m._Marker_key = r._Marker_key
and r.jnum in (24195, 24194, 34136, 29126, 29505, 37748, 37749, 37750, 58777, 59376, 34105, 34106, 55473, 55472, 55474, 37732)
go

set nocount off
go

print ""
print "Mapped Markers w/out a Mapping Reference"
print "(excludes UN, MT, withdrawn markers, cytogenetic markers)"
print "(excludes Markers referenced by mapping panel database releases)"
print ""

select m.symbol, m.chromosome, substring(t.name, 1, 20)
from #markers me, MRK_Marker m, MRK_Chromosome c, MRK_Types t
where me._Marker_key = m._Marker_key
and m._Organism_key = c._Organism_key
and m.chromosome = c.chromosome
and m._Marker_Type_key = t._Marker_Type_key
and not exists (select 1 from #exclude e
where m._Marker_key = e._Marker_key)
order by m._Marker_Type_key, c.sequenceNum, m.symbol
go

print ""
print "Mapped Markers w/out a Mapping Reference"
print "(excludes UN, MT, withdrawn markers, cytogenetic markers)"
print "(excludes Markers referenced by mapping panel database releases)"
print "(only includes Markers broadcast 05/25/2000 or later)"
print ""

select m.symbol, m.chromosome, substring(t.name, 1, 20), h.jnumID
from #markers me, MRK_Marker m, MRK_Chromosome c, MRK_Types t, MRK_History_Ref_View h
where me._Marker_key = m._Marker_key
and m._Marker_Type_key = t._Marker_Type_key
and m._Organism_key = c._Organism_key
and m.chromosome = c.chromosome
and m._Marker_Key = h._Marker_key
and h._Marker_Event_key = 1
and h.event_date >= "05/24/2000"
and not exists (select 1 from #exclude e
where m._Marker_key = e._Marker_key)
order by m._Marker_Type_key, c.sequenceNum, m.symbol
go

