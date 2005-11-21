print ""
print "Orthologies w/ Conserved Map Location and Chromosome = UN"
print ""

select m.symbol, o.commonName, jnum = aa.accID
from HMD_Homology_Marker hm, MRK_Marker m, MGI_Organism o, HMD_Homology_Assay a, HMD_Homology h, ACC_Accession aa
where hm._Homology_key = a._Homology_key
and a._Assay_key = 14
and hm._Marker_key = m._Marker_key
and m.chromosome = "UN"
and m._Organism_key = o._Organism_key
and hm._Homology_key = h._Homology_key
and h._Refs_key = aa._Object_key
and aa._LogicalDB_key = 1
and aa.prefixPart = 'J:'
order by hm._Homology_key, m.symbol
go

