set nocount on
go

/* select all GXD Genotype annotations */
select distinct e._Genotype_key, e._Refs_key
into #gxd
from GXD_Expression e
go

/* select all MPm/Genotype Reference annotations */
select distinct a._Object_key, e._Refs_key
into #ap
from VOC_Annot a, VOC_Evidence e
where a._AnnotType_key = 1002
and a._Annot_key = e._Annot_key
go

/* select those that share the same reference */
/* exclude Not Specified genotype */
select genoGXD = g._Genotype_key, genoAP = a._Object_key, g._Refs_key
into #shareRef
from #gxd g, #ap a
where g._Refs_key = a._Refs_key
and g._Genotype_key > 0
go

/* select unique genotypes */
select distinct genoGXD into #uniqueGXD from #shareRef 
go
select distinct genoAP into #uniqueAP from #shareRef
go

/* select all alleles */
select s.genoGXD, a._Allele_key_1
into #gxdAlleles
from #uniqueGXD s, GXD_AllelePair a
where s.genoGXD = a._Genotype_key
union all
select s.genoGXD, a._Allele_key_2
from #uniqueGXD s, GXD_AllelePair a
where s.genoGXD = a._Genotype_key
and a._Allele_key_2 is not null
go

select s.genoAP, a._Allele_key_1
into #apAlleles
from #uniqueAP s, GXD_AllelePair a
where s.genoAP = a._Genotype_key
union all
select s.genoAP, a._Allele_key_2
from #uniqueAP s, GXD_AllelePair a
where s.genoAP = a._Genotype_key
and a._Allele_key_2 is not null
go

/* calculate allele counts */
select s.genoGXD, alleleCount = count(s._Allele_key_1)
into #gxdCount
from #gxdAlleles s
group by s.genoGXD
go

select s.genoAP, alleleCount = count(s._Allele_key_1)
into #apCount
from #apAlleles s
group by s.genoAP
go

/* select those that have the same allele pair counts */
select s.*
into #sameCount
from #shareRef s, #gxdCount g, #apcount a
where s.genoGXD = g.genoGXD
and s.genoAP = a.genoAP
and g.alleleCount = a.alleleCount
go

/* select those that do not have the same allele pairs */
/* TR 10093 */
/* should be able to remove the checks on sequenceNum */
/* however, as long as the sequenceNum are the same, the allele pair */
/* match should work correctly */
/* for now, leave the sequenceNum check in... */

select s.*
into #diffAlleles
from #shareRef s, #sameCount c
where s.genoGXD = c.genoGXD
and s.genoAP = c.genoAP
and (
exists (select 1 from GXD_AllelePair a1, GXD_AllelePair a2
where s.genoGXD = a1._Genotype_key
and s.genoAP = a2._Genotype_key
and a1.sequenceNum = a2.sequenceNum
and a1._Allele_key_1 != a2._Allele_key_1)
or exists (select 1 from GXD_AllelePair a1, GXD_AllelePair a2
where s.genoGXD = a1._Genotype_key
and s.genoAP = a2._Genotype_key
and a1.sequenceNum = a2.sequenceNum
and a1._Allele_key_2 != a2._Allele_key_2)
)
go

/* select those that have the same alleles and the same strain names */
select s.*
into #sameStrain
from #sameCount s, GXD_Genotype g1, PRB_Strain s1, GXD_Genotype g2, PRB_Strain s2
where s.genoGXD = g1._Genotype_key
and s.genoAP = g2._Genotype_key
and g1._Strain_key = s1._Strain_key
and g2._Strain_key = s2._Strain_key
and s1.strain = s2.strain
and not exists (select 1 from #diffAlleles a where s.genoGXD = a.genoGXD and s.genoAP = a.genoAP)
go

/* select those that have the same alleles and where there is not already */
/* another GXD/AP genotype that does match */
select jnum = a.accID, gxdStrain = s1.strain, apStrain = s2.strain, s.genoGXD
into #toPrint1
from #sameCount s, GXD_Genotype g1, PRB_Strain s1, GXD_Genotype g2, PRB_Strain s2, ACC_Accession a
where s.genoGXD = g1._Genotype_key
and s.genoAP = g2._Genotype_key
and g1._Strain_key = s1._Strain_key
and g2._Strain_key = s2._Strain_key
and s1.strain != s2.strain
and not exists (select 1 from #diffAlleles a where s.genoGXD = a.genoGXD and s.genoAP = a.genoAP)
and not exists (select 1 from #sameStrain a where s.genoGXD = a.genoGXD and s._Refs_key = a._Refs_key)
and s._Refs_key = a._Object_key
and a._MGIType_key = 1
and a._LogicalDB_key = 1
and a.prefixPart = "J:"
go

set nocount off
go

print ""
print "References where GXD and Pheno differ in Genotype"
print ""

select t.jnum, substring(t.gxdStrain, 1, 75) "GXD Strain", substring(t.apStrain, 1, 75) "A&P Strain", a1.symbol, a2.symbol
from #toPrint1 t, GXD_AllelePair a, ALL_Allele a1, ALL_Allele a2
where t.genoGXD = a._Genotype_key
and a._Allele_key_1 = a1._Allele_key
and a._Allele_key_2 = a2._Allele_key
order by t.jnum
go

