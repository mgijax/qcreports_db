/* TR 2920 */
/* Comparison of orthologous relationships between MGD and LocusLink */
/* Uses the LL file homol_seq_pairs which is downloaded from their */
/* ftp site using the locuslinkload product */
/* This file is dumped into tempdb..LLHomology */

print ""
print "The mouse/human orthologous pairs that LocusLink is reporting that we are"
print "not reporting in our homology data, where we have neither the mouse nor the"
print "human member of the pair."
print ""

print ""
print "HUMAN AND MOUSE SYMBOLS ARE NOT THE SAME"
print ""

select h.*
from tempdb..LLHomology h
where h.species1 = "Homo sapiens"
and h.species2 = "Mus musculus"
and h.symbol1 != h.symbol2
and not exists (select 1 from MRK_Marker m
where m._Species_key = 1
and m.symbol = h.symbol2)
union
select h.*
from tempdb..LLHomology h
where h.species1 = "Homo sapiens"
and h.species2 = "Mus musculus"
and h.symbol1 != h.symbol2
and 
not exists (select 1 from MRK_Marker m
where m._Species_key = 2
and m.symbol = h.symbol1)
order by h.symbol1
go

