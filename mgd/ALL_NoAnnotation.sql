
print ""
print "Alleles w/ 'Associated Phenotype Controlled Terms' in Notes"
print "and no PhenoSlim or MP annotation"
print ""

select distinct a.symbol
from ALL_Note n, ALL_Allele a
where n.note like '%Associated Phenotype Controlled Terms%'
and n._Allele_key = a._Allele_key
and not exists (select 1 from GXD_AlleleGenotype g, VOC_Annot v
where a._Allele_key = g._Allele_key
and g._Genotype_key = v._Object_key
and v._AnnotType_key in (1001, 1002))
order by a.symbol
go


