set nocount on
go

select m._Marker_key, m.symbol, mgiID = a1.accID, refSeq = a2.accID
into #markers
from MRK_Marker m, MRK_Acc_View a1, MRK_Acc_View a2
where m._Species_key = 1
and m.symbol not like '%Rik'
and m.symbol not like '%-rs'
and m.symbol not like '%-ps'
and m.name not like '%DNA segment%'
and m._Marker_key = a1._Object_key
and a1._LogicalDB_key = 1
and a1.preferred = 1
and m._Marker_key = a2._Object_key
and a2._LogicalDB_key = 27
and not exists (select 1 from
HMD_Homology r1, HMD_Homology_Marker h1, 
HMD_Homology r2, HMD_Homology_Marker h2, MRK_Marker m2
where m._Marker_key = h1._Marker_key 
and h1._Homology_key = r1._Homology_key 
and r1._Class_key = r2._Class_key 
and r2._Homology_key = h2._Homology_key 
and h2._Marker_key = m2._Marker_key 
and m2._Species_key = 2)
go

print ""
print "Mouse Genes w/ RefSeq but No Human Homology"
print "(excludes RIKEN, ESTs, DNA Segments, Related Sequences, Pseudogenes)"
print "List of Mouse Genes where symbol matches a Human LocusLink symbol"
print ""

select m.*, llsymbol = l.osymbol, stype = "O", l.locusID
from #markers m, tempdb..LL l
where m.symbol = l.osymbol
and l.taxID = 9606
union
select m.*, llsymbol = l.isymbol, stype = "I", l.locusID
from #markers m, tempdb..LL l
where m.symbol = l.isymbol
go

