set nocount on
go

select a._Assay_key, label = substring(s.specimenLabel,1,75)
into #insitu
from GXD_Assay a, GXD_Specimen s, GXD_Genotype g, GXD_AllelePair ap
where a._Assay_key = s._Assay_key
and s._Genotype_key = g._Genotype_key
and g._Genotype_key = ap._Genotype_key
and ap._Allele_key_2 is null
go

select a._Assay_key, label = substring(s.laneLabel,1,75)
into #gel
from GXD_Assay a, GXD_GelLane s, GXD_Genotype g, GXD_AllelePair ap
where a._Assay_key = s._Assay_key
and s._Genotype_key = g._Genotype_key
and g._Genotype_key = ap._Genotype_key
and ap._Allele_key_2 is null
go

set nocount off
go

print ""
print "InSitu Assays w/ missing Allele 2"
print ""

select a.mgiID "Assay MGI ID", a.jnumID, i.label
from #insitu i, GXD_Assay_View a
where i._Assay_key = a._Assay_key
go

print ""
print "Gel Assays w/ missing Allele 2"
print ""

select a.mgiID "Assay MGI ID", a.jnumID, g.label
from #gel g, GXD_Assay_View a
where g._Assay_key = a._Assay_key
go

