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
and m._Species_key = 1)
go

set nocount off
go

print ""
print "Homology Records w/out Mouse Genes"
print ""

select distinct h._Class_key, h.symbol, h.species, h.jnumID
from #class c, HMD_Homology_View h
where c._Class_key = h._Class_key
order by c._Class_key
go

