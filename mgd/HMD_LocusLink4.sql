/* TR 2920 */
/* Comparison of orthologous relationships between MGD and LocusLink */
/* Uses the LL file homol_seq_pairs which is downloaded from their */
/* ftp site using the locuslinkload product */
/* This file is dumped into tempdb..LLHomology */

print ""
print "The mouse/human orthologous pairs that LocusLink is reporting that we are"
print "not reporting, where we are reporting orthology regarding the mouse but no"
print "human member appears in our homology class."
print ""

select distinct h.species1, h.locusID1, symbol1 = substring(h.symbol1, 1, 25), h.refSeq1, h.length1,
h.species2, h.locusID2, symbol2 = substring(h.symbol2, 1, 25), h.refSeq2, h.length2,
h.maxidentity, h.avgidentity, h.lenmatchseq
from tempdb..LLHomology h, HMD_Homology_Marker hm1, MRK_Marker m1, HMD_Homology h1
where h.species1 = "Homo sapiens"
and h.species2 = "Mus musculus"
and h.symbol2 = m1.symbol
and m1._Organism_key = 1
and m1._Marker_key = hm1._Marker_key
and hm1._Homology_key = h1._Homology_key
and not exists (select 1 from
HMD_Homology h2, HMD_Homology_Marker hm2, MRK_Marker m2
where h1._Class_key = h2._Class_key
and h2._Homology_key = hm2._Homology_key
and hm2._Marker_key = m2._Marker_key
and m2._Organism_key = 2)
order by h.symbol1
go

