print ""
print "Orphan Genotypes (can be deleted)"
print ""

select g._Genotype_key, strain = substring(s.strain, 1, 65)
from GXD_Genotype g, PRB_Strain s
where not exists (select 1 from GXD_Expression a where g._Genotype_key = a._Genotype_key)
and not exists (select 1 from GXD_GelLane a where g._Genotype_key = a._Genotype_key)
and not exists (select 1 from GXD_Specimen a where g._Genotype_key = a._Genotype_key)
and not exists (select 1 from VOC_Annot a where g._Genotype_key = a._Object_key and a._AnnotType_key in (1001,1002))
and not exists (select 1 from PRB_Strain_Genotype a where g._Genotype_key = a._Genotype_key)
and g._Strain_key = s._Strain_key
order by s.strain
go
