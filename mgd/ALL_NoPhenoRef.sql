
/**/
/* TR 10024 */
/* allels that are involved in a genotype */
/* that has an annotation containing */
/*     "no phenotypic analysis" MP:0003012 */
/*     "no abnormal phenotype detected" MP:0002169 */
/* contains references where reference type in */
/*     indexed */
/*     priority indexed */
/**/

print ""
print "Alleles that are involved in genotypes where"
print ""
print "annotations contain"
print "    no phenotypic analysis, MP:0003012"
print "    no abnormal phenotype detected, MP:0002169"
print ""
print "references contain"
print "    indexed"
print "    priority indexed"
print ""

select distinct aa.symbol, term = substring(t.term, 1, 35)
from ALL_Allele aa, GXD_AlleleGenotype g, VOC_Annot a, VOC_Term t
where aa._Allele_key = g._Allele_key
and g._Genotype_key = a._Object_key
and a._AnnotType_key = 1002
and a._Term_key in (83412,293594)
and a._Term_key = t._Term_key
and exists (select 1 from MGI_Reference_Allele_View r
where aa._Allele_key = r._Object_key
and r.assocType in ('Priority Index', 'Indexed'))
order by aa.symbol
go

