/* TR 2920 */
/* Comparison of orthologous relationships between MGD and LocusLink */
/* Uses the LL file homol_seq_pairs which is downloaded from their */
/* ftp site using the locuslinkload product */
/* This file is dumped into tempdb..LLHomology */

set nocount on
go

select h.species1, h.locusID1, symbol1 = substring(h.symbol1, 1, 25), h.refSeq1, h.length1,
h.species2, h.locusID2, symbol2 = substring(h.symbol2, 1, 25), h.refSeq2, h.length2,
h.maxidentity, h.avgidentity, h.lenmatchseq
into #homology
from tempdb..LLHomology h, tempdb..LL l
where h.species1 = "Homo sapiens"
and h.species2 = "Mus musculus"
and h.symbol1 != h.symbol2
and h.locusID1 = l.locusID
and l.osymbol is not null
go

set nocount off
go

print ""
print "The mouse/human orthologous pairs that LocusLink is reporting that we are"
print "not reporting in our homology data, where we have neither the mouse nor the"
print "OFFICIAL human member of the pair."
print ""

print ""
print "HUMAN AND MOUSE SYMBOLS ARE NOT THE SAME"
print "Human symbols are Official"
print "Mouse symbols are RIKEN"
print ""

select h.*
from #homology h
where h.symbol2 like "%Rik"
and not exists (select 1 from MRK_Marker m
where m._Species_key = 1
and m.symbol = h.symbol2)
union
select h.*
from #homology h
where h.symbol2 like "%Rik"
and not exists (select 1 from MRK_Marker m
where m._Species_key = 2
and m.symbol = h.symbol1)
order by h.symbol1
go

print ""
print "HUMAN AND MOUSE SYMBOLS ARE NOT THE SAME"
print "Human symbols are Official"
print "Mouse symbols are non-RIKEN"
print ""

select h.*
from #homology h
where h.symbol2 not like "%Rik"
and not exists (select 1 from MRK_Marker m
where m._Species_key = 1
and m.symbol = h.symbol2)
union
select h.*
from #homology h
where h.symbol2 not like "%Rik"
and not exists (select 1 from MRK_Marker m
where m._Species_key = 2
and m.symbol = h.symbol1)
order by h.symbol1
go

