
print ""
print "Alleles with Immune System Annotations"
print ""

select distinct a.symbol
from ALL_Allele a, ALL_Note_General_View n
where a._Allele_key = n._Allele_key
and n.note like '%immune system:%'
union
select distinct a.symbol
from ALL_Allele a, GXD_AlleleGenotype g, VOC_Annot_View v
where a._Allele_key = g._Allele_key
and g._Genotype_key = v._Object_key
and v._AnnotType_key = 1001
and v.term like '%immune system:%'
union
select distinct a.symbol
from ALL_Allele a, GXD_AlleleGenotype g, VOC_Annot_View v
where a._Allele_key = g._Allele_key
and g._Genotype_key = v._Object_key
and v._AnnotType_key = 1002
and v.term like '%immune system:%'
order by a.symbol
go

