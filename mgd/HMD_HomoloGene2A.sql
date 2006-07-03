/* TR 2920 */
/* Comparison of orthologous relationships between MGD and HomoloGene */
/* Uses the HomologGene file homologene.data which is downloaded from their */
/* ftp site using the entrezgeneload product */
/* This file is dumped into radar..DP_HomoloGene */

set nocount on
go

select species1 = "human", geneID1 = h1.geneID, symbol1 = h1.symbol,
species2 = "mouse", geneID2 = h2.geneID, symbol2 = h2.symbol
into #homology
from radar..DP_HomoloGene h1, radar..DP_HomoloGene h2, radar..DP_EntrezGene_Info e
where h1.taxID = 9606
and h1.groupID = h2.groupID
and h2.taxID = 10090
and h1.symbol != h2.symbol
and h1.geneID = e.geneID
go

set nocount off
go

print ""
print "The mouse/human orthologous pairs that HomoloGene is reporting that we are"
print "not reporting in our orthology data, where we have neither the mouse nor the"
print "OFFICIAL human member of the pair."
print ""

print ""
print "HUMAN AND MOUSE SYMBOLS ARE NOT THE SAME"
print "Human symbols are Official"
print "Mouse symbols are RIKEN"
print ""

select h.*
from #homology h, radar..DP_EntrezGene_Info e
where h.symbol2 like "%Rik" 
and h.symbol1 = e.symbol
and e.taxID = 9606
and e.status = "O"
and not exists (select 1 from MRK_Marker m where m._Organism_key = 1 and m.symbol = h.symbol2)
and not exists (select 1 from MRK_Marker m where m._Organism_key = 2 and m.symbol = h.symbol1)
order by h.symbol1
go

print ""
print "HUMAN AND MOUSE SYMBOLS ARE NOT THE SAME"
print "Human symbols are Official"
print "Mouse symbols are non-RIKEN"
print ""

select h.*
from #homology h, radar..DP_EntrezGene_Info e
where h.symbol2 not like "%Rik"
and h.symbol1 = e.symbol
and e.taxID = 9606
and e.status = "O"
and not exists (select 1 from MRK_Marker m where m._Organism_key = 1 and m.symbol = h.symbol2)
and not exists (select 1 from MRK_Marker m where m._Organism_key = 2 and m.symbol = h.symbol1)
order by h.symbol1
go

