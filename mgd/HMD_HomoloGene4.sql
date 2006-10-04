/* TR 2920 */
/* Comparison of orthologous relationships between MGD and HomoloGene */
/* Uses the HomologGene file homologene.data which is downloaded from their */
/* ftp site using the entrezgeneload product */
/* This file is dumped into radar..DP_HomoloGene */

print ""
print "The mouse/human orthologous pairs that HomoloGene is reporting that we are"
print "not reporting, where we are reporting orthology regarding the mouse but no"
print "human member appears in our orthology class."
print ""

select species1 = "human", geneID1 = h1.geneID, symbol1 = h1.symbol,
species2 = "mouse", geneID2 = h2.geneID, symbol2 = h2.symbol
from radar..DP_HomoloGene h1, radar..DP_HomoloGene h2,
MRK_Homology_Cache hm1, MRK_Marker m1
where h1.taxID = 9606
and h1.groupID = h2.groupID
and h2.taxID = 10090
and h2.symbol = m1.symbol
and m1._Organism_key = 1
and m1._Marker_key = hm1._Marker_key
and not exists (select 1 from MRK_Homology_Cache hm2
where hm1._Class_key = hm2._Class_key
and hm2._Organism_key = 2)
order by h1.symbol1
go

