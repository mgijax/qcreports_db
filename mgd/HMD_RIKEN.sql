set nocount on
go

select distinct a.accID, msymbol = m2.symbol, mchr = m2.chromosome,
hsymbol = m1.symbol, hchr = m1.chromosome + m1.cytogeneticOffset,
c.sequenceNum
into #homology
from HMD_Homology r1, HMD_Homology_Marker h1, 
HMD_Homology r2, HMD_Homology_Marker h2, 
MRK_Marker m1, MRK_Marker m2, MRK_Chromosome c, ACC_Accession a 
where m1._Organism_key = 2 
and m1._Marker_key = h1._Marker_key 
and h1._Homology_key = r1._Homology_key 
and r1._Class_key = r2._Class_key 
and r2._Homology_key = h2._Homology_key 
and h2._Marker_key = m2._Marker_key 
and m2._Organism_key = 1 
and m2.symbol like '%Rik'
and m2._Marker_key = a._Object_key 
and a._MGIType_key = 2 
and a.prefixPart = "MGI:" 
and a._LogicalDB_key = 1
and a.preferred = 1 
and m1._Organism_key = c._Organism_key 
and m1.chromosome = c.chromosome 
go

select h.*, type = "O"
into #results
from #homology h, radar..DP_LL l
where h.hsymbol = l.osymbol
and l.taxID = 9606
union
select h.*, type = "I"
from #homology h, radar..DP_LL l
where h.hsymbol = l.isymbol
and l.taxID = 9606
union
select h.*, type = "?"
from #homology h
where not exists (select 1 from radar..DP_LL l
where l.taxID = 9606 and (h.hsymbol = l.osymbol or h.hsymbol = l.isymbol))
go

set nocount off
go

print ""
print "Mouse/Human Homologies involving RIKEN Symbols"
print ""

select
accID "Mouse MGI Acc ID", msymbol "Mouse Symbol", mchr "Mouse Chr", 
type "Type", hsymbol "Human Symbol", hchr "Human Chr"
from #results
order by type desc, sequenceNum, hsymbol
go

