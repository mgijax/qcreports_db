print ""
print "Orthologies w/ Conserved Map Location and Chromosome = UN"
print ""

select h.symbol, h.commonName, h.jnum
from HMD_Homology_View h, HMD_Homology_Assay a
where h._Homology_key = a._Homology_key
and a._Assay_key = 14
and h.chromosome = "UN"
order by h._Homology_key, h.symbol
go

