print ""
print "Splits"
print ""

select distinct m.symbol, m.name
from MRK_Marker m
where m._Species_key = 1
and m._Marker_Status_key = 2
and m.name like 'withdrawn, = %,%'
order by m.chromosome, m.symbol
go

print ""
print "Withdrawals w/ Additional Information"
print ""

select distinct m.symbol, m.chromosome, label = 'Mapping'
from MRK_Marker m, MLD_Marker g
where m._Marker_Status_key = 2 and m._Marker_key = g._Marker_key
union
select distinct m.symbol, m.chromosome, label = 'Mapping'
from MRK_Marker m, MLD_Expt_Marker g
where m._Marker_Status_key = 2 and m._Marker_key = g._Marker_key
union
select distinct m.symbol, m.chromosome, label = 'Probe'
from MRK_Marker m, PRB_Marker g
where m._Marker_Status_key = 2 and m._Marker_key = g._Marker_key
union
select distinct m.symbol, m.chromosome, label = 'Homology'
from MRK_Marker m, HMD_Homology_Marker g
where m._Marker_Status_key = 2 and m._Marker_key = g._Marker_key
union
select distinct m.symbol, m.chromosome, label = 'Classes'
from MRK_Marker m, MRK_Classes g
where m._Marker_Status_key = 2 and m._Marker_key = g._Marker_key
union
select distinct m.symbol, m.chromosome, label = 'Alleles'
from MRK_Marker m, ALL_Allele g
where m._Marker_Status_key = 2 and m._Marker_key = g._Marker_key
select distinct m.symbol, m.chromosome, label = 'MLC'
from MRK_Marker m, MLC_Text_edit g
where m._Marker_Status_key = 2 and m._Marker_key = g._Marker_key
select distinct m.symbol, m.chromosome, label = 'GO'
from MRK_Marker m, VOC_Annot g
where m._Marker_Status_key = 2 and m._Marker_key = g._Object_key
and g._AnnotType_key = 1000
order by m.chromosome, m.symbol
go

