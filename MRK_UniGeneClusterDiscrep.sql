select accID, _Object_key
into #ug
from ACC_Accession
where _MGIType_key = 2
and _LogicalDB_key = 23

select accID, cntChromosome=count(distinct chromosome)
into #ugc
from #ug u, MRK_Marker m
where u._Object_key = m._Marker_key
group by accID
having count(distinct chromosome)>1

print ""
print "NOTE:"
print "Some associations are result of 'faulty' UniGene clustering"
print "not MGI errors."
print ""

select "Distinct UniGene IDs"=count(*) from #ugc

select #ugc.accID, chromosome, symbol
from #ugc, #ug, MRK_Marker m
where #ugc.accID = #ug.accID
and #ug._Object_key = m._Marker_key
order by accID, chromosome, symbol

go

