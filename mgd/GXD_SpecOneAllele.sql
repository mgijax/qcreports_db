set nocount on
go

select _Genotype_key 
into #genotypes 
from GXD_AllelePair
go

select * 
into #onepair 
from #genotypes
group by _Genotype_key having count(*) = 1
go

set nocount off
go

print ""
print "InSitu Specimens with Single Allele Genotypes"
print ""

select a.mgiID "Assay MGI ID", a.jnumID, substring(s.specimenLabel,1,75) "Label"
from #genotypes g, GXD_Assay_View a, GXD_Specimen s
where g._Genotype_key = s._Genotype_key
and s._Assay_key = a._Assay_key
order by a.jnumID
go

print ""
print "Gel Lane Specimens with Single Allele Genotypes"
print ""

select a.mgiID "Assay MGI ID", a.jnumID, substring(s.laneLabel,1,75) "Label"
from #genotypes g, GXD_Assay_View a, GXD_GelLane s
where g._Genotype_key = s._Genotype_key
and s._Assay_key = a._Assay_key
order by a.jnumID
go

