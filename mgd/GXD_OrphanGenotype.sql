print ""
print "Orphan Genotypes (can be deleted)"
print ""

select g._Genotype_key, strain = substring(g.strain, 1, 65)
from GXD_Genotype_View g
where not exists (select 1 from GXD_AlleleGenotype a where g._Genotype_key = a._Genotype_key)
and not exists (select 1 from GXD_Expression a where g._Genotype_key = a._Genotype_key)
and not exists (select 1 from GXD_GelLane a where g._Genotype_key = a._Genotype_key)
and not exists (select 1 from GXD_Specimen a where g._Genotype_key = a._Genotype_key)
and not exists (select 1 from VOC_Annot a where g._Genotype_key = a._Object_key and a._AnnotType_key in (1001,1002))
order by g.strain
go
