set nocount on
go

select distinct mkey = m1._Marker_key, msymbol = m1.symbol, mchr = m1.chromosome,
hsymbol = m2.symbol, hchr = m2.chromosome + m2.cytogeneticOffset, c.sequenceNum
into #homology1
from HMD_Homology r1, HMD_Homology_Marker h1, 
HMD_Homology r2, HMD_Homology_Marker h2, 
MRK_Marker m1, MRK_Marker m2, MRK_Chromosome c
where m1._Organism_key = 1 
and m1.symbol like '%Rik'
and m1._Marker_key = h1._Marker_key 
and h1._Homology_key = r1._Homology_key 
and r1._Class_key = r2._Class_key 
and r2._Homology_key = h2._Homology_key 
and h2._Marker_key = m2._Marker_key 
and m2._Organism_key = 2 
and m2._Organism_key = c._Organism_key 
and m2.chromosome = c.chromosome 
go

create index idx1 on #homology1(mKey)
go

select distinct a.accID, h.*
into #homology2
from #homology1 h, ACC_Accession a
where h.mkey = a._Object_key 
and a._MGIType_key = 2 
and a.prefixPart = "MGI:" 
and a._LogicalDB_key = 1
and a.preferred = 1 
go

create index idx1 on #homology2(hsymbol)
go

select h.*, type = "O"
into #results
from #homology2 h, radar..DP_LL l
where h.hsymbol = l.osymbol
and l.taxID = 9606
union
select h.*, type = "I"
from #homology2 h, radar..DP_LL l
where h.hsymbol = l.isymbol
and l.taxID = 9606
union
select h.*, type = "?"
from #homology2 h
where not exists (select 1 from radar..DP_LL l
where l.taxID = 9606 and h.hsymbol = l.osymbol)
and not exists (select 1 from radar..DP_LL l
where l.taxID = 9606 and h.hsymbol = l.isymbol)
go

create index idx1 on #results(type)
create index idx2 on #results(sequenceNum)
create index idx3 on #results(hsymbol)
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

