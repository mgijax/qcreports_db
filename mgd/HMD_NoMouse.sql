set nocount on
go

select distinct hc._Class_key
into #class
from HMD_Class hc
where not exists (select 1 
from HMD_Homology h, HMD_Homology_Marker hm, MRK_Marker m
where hc._Class_key = h._Class_key
and h._Homology_key = hm._Homology_key
and hm._Marker_key = m._Marker_key
and m._Organism_key = 1)
go

select distinct h._Class_key, h.symbol, h.species, h.jnumID, h._Organism_key
into #homology
from #class c, HMD_Homology_View h
where c._Class_key = h._Class_key
order by c._Class_key
go

set nocount off
go

print ""
print "Homology Records w/out Mouse Genes"
print "(The mouse symbol is listed if it is the same as one of the other species)"
print ""

select distinct h._Class_key, h.symbol, m.symbol "mouse symbol", h.species, h.jnumID
from #homology h, MRK_Marker m
where h.symbol not like '*%'
and h.symbol *= m.symbol
and m._Organism_key = 1
union
select distinct h._Class_key, h.symbol, m.symbol, h.species, h.jnumID
from #homology h, MRK_Marker m
where h.symbol like '*%'
and substring(h.symbol, 2, char_length(h.symbol) - 2) *= m.symbol
and m._Organism_key = 1
order by h._Class_key
go

