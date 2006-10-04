set nocount on
go

select distinct hc._Class_key
into #class
from MRK_Homology_Cache hc
where not exists (select 1 
from MRK_Homology_Cache hc2
where hc._Class_key = hc2._Class_key
and hc2._Organism_key = 1)
go

select distinct h._Class_key, h.symbol, organism = h.commonName, h.jnumID, h._Organism_key
into #homology
from #class c, HMD_Homology_View h
where c._Class_key = h._Class_key
order by c._Class_key
go

set nocount off
go

print ""
print "Orthology Records w/out Mouse Genes"
print "(The mouse symbol is listed if it is the same as one of the other organism)"
print ""

select distinct h._Class_key, substring(h.symbol,1,30) "human symbol", substring(m.symbol,1,30) "mouse symbol", h.organism, h.jnumID
from #homology h, MRK_Marker m
where h.symbol not like '*%'
and h.symbol *= m.symbol
and m._Organism_key = 1
union
select distinct h._Class_key, substring(h.symbol,1,30), substring(m.symbol,1,30), h.organism, h.jnumID
from #homology h, MRK_Marker m
where h.symbol like '*%'
and substring(h.symbol, 2, char_length(h.symbol) - 2) *= m.symbol
and m._Organism_key = 1
order by h._Class_key
go

