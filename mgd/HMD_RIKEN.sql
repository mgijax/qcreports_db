set nocount on
go

select mkey = m._Marker_key, msymbol = m.symbol, mchr = m.chromosome
into #markers
from MRK_Marker m
where m._Organism_key = 1
and m.symbol like '%Rik'
go

create index idx1 on #markers(mkey)
go

select hkey = m._Marker_key, hsymbol = m.symbol, hchr = m.chromosome + m.cytogeneticOffset, c.sequenceNum
into #hmarkers
from MRK_Marker m, MRK_Chromosome c
where m._Organism_key = 2
and m._Organism_key = c._Organism_key
and m.chromosome = c.chromosome
go

create index idx1 on #hmarkers(hkey)
go

select distinct m1.mkey, m1.msymbol, m1.mchr, m2.hsymbol, m2.hchr, m2.sequenceNum
into #homology1
from #markers m1, #hmarkers m2, 
HMD_Homology r1, HMD_Homology_Marker h1, 
HMD_Homology r2, HMD_Homology_Marker h2
where m1.mkey = h1._Marker_key 
and h1._Homology_key = r1._Homology_key 
and r1._Class_key = r2._Class_key 
and r2._Homology_key = h2._Homology_key 
and h2._Marker_key = m2.hkey
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
from #homology2 h, radar_2..DP_EntrezGene_Info e
where h.hsymbol = e.symbol
and e.taxID = 9606
go

insert into #results
select h.*, type = "I"
from #homology2 h, radar_2..DP_EntrezGene_Synonym es, radar_2..DP_EntrezGene_Info e
where h.hsymbol = es.synonym
and es.geneID = e.geneID
and e.taxID = 9606
go

insert into #results
select h.*, type = "?"
from #homology2 h
where not exists (select 1 from radar_2..DP_EntrezGene_Info e
where e.taxID = 9606 and h.hsymbol = e.symbol)
and not exists (select 1 from radar_2..DP_EntrezGene_Synonym es, radar_2..DP_EntrezGene_Info e
where e.taxID = 9606 and e.geneID = es.geneID
and h.hsymbol = es.synonym)
go

create index idx1 on #results(type)
create index idx2 on #results(sequenceNum)
create index idx3 on #results(hsymbol)
go

set nocount off
go

print ""
print "Mouse/Human Orthologies involving RIKEN Symbols"
print ""

select
accID "Mouse MGI Acc ID", msymbol "Mouse Symbol", mchr "Mouse Chr", 
type "Type", hsymbol "Human Symbol", hchr "Human Chr"
from #results
order by type desc, sequenceNum, hsymbol
go

