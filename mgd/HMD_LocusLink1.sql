/* TR 2920 */
/* Comparison of orthologous relationships between MGD and HomoloGene */
/* Uses the HomologGene file homologene.data which is downloaded from their */
/* ftp site using the locuslinkload product */
/* This file is dumped into radar..DP_LLHomology */

set nocount on
go

select species1 = "human", geneID1 = h1.geneID, symbol1 = h1.symbol,
species2 = "mouse", geneID2 = h2.geneID, symbol2 = h2.symbol
into #homology
from radar..DP_LLHomology h1, radar..DP_LLHomology h2, radar..DP_EntrezGene_Info e
where h1.taxID = 9606
and h1.groupID = h2.groupID
and h2.taxID = 10090
and h1.symbol = h2.symbol
and h1.geneID = e.geneID
go

set nocount off
go

print ""
print "The mouse/human orthologous pairs that HomoloGene is reporting that we are"
print "not reporting in our orthology data, where we have neither the mouse nor the"
print "human member of the pair."
print ""

print "HUMAN AND MOUSE SYMBOLS ARE THE SAME"
print ""

select h.*
from #homology h
where not exists (select 1 from MRK_Marker m where m._Organism_key = 1 and m.symbol = h.symbol2)
and not exists (select 1 from MRK_Marker m where m._Organism_key = 2 and m.symbol = h.symbol1)
order by h.symbol1
go

