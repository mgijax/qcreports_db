print ""
print "Mouse/Human Homologies involving RIKEN Symbols"
print ""

select distinct 
a.accID "Mouse MGI Acc ID",
m2.symbol "Mouse Symbol",
m2.chromosome "Mouse Chr", 
m1.symbol "Human Symbol", 
m1.chromosome + m1.cytogeneticOffset "Human Chr"
from HMD_Homology r1, HMD_Homology_Marker h1, 
HMD_Homology r2, HMD_Homology_Marker h2, 
MRK_Marker m1, MRK_Marker m2, MRK_Chromosome c, ACC_Accession a 
where m1._Species_key = 2 
and m1._Marker_key = h1._Marker_key 
and h1._Homology_key = r1._Homology_key 
and r1._Class_key = r2._Class_key 
and r2._Homology_key = h2._Homology_key 
and h2._Marker_key = m2._Marker_key 
and m2._Species_key = 1 
and m2.symbol like '%Rik'
and m2._Marker_key = a._Object_key 
and a._MGIType_key = 2 
and a.prefixPart = "MGI:" 
and a.preferred = 1 
and m1._Species_key = c._Species_key 
and m1.chromosome = c.chromosome 
order by c.sequenceNum, m2.symbol
go

