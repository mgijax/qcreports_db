
print ""
print "Alleles w/ 'Associated Phenotype Controlled Terms' in Notes with no MP annotation"
print ""

select distinct a.symbol
from MGI_Note n, MGI_NoteChunk nc, ALL_Allele a
where nc.note like '%Associated Phenotype Controlled Terms%'
and n._Object_key = a._Allele_key
and n._MGIType_key = 11
and n._Note_key = nc._Note_key
and not exists (select 1 from GXD_AlleleGenotype g, VOC_Annot v
where a._Allele_key = g._Allele_key
and g._Genotype_key = v._Object_key
and v._AnnotType_key 1002
order by a.symbol
go


