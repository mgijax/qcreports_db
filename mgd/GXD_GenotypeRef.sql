/* select all GXD Genotype annotations */
select distinct e._Genotype_key, e._Refs_key
INTO TEMPORARY TABLE gxd
from GXD_Expression e
;

/* select all MPm/Genotype Reference annotations */
select distinct a._Object_key, e._Refs_key
INTO TEMPORARY TABLE ap
from VOC_Annot a, VOC_Evidence e
where a._AnnotType_key = 1002
and a._Annot_key = e._Annot_key
;

/* select those that share the same reference */
/* exclude Not Specified genotype */
select g._Genotype_key as genoGXD, a._Object_key as genoAP, g._Refs_key
INTO TEMPORARY TABLE shareRef
from gxd g, ap a
where g._Refs_key = a._Refs_key
and g._Genotype_key > 0
;

/* select unique genotypes */
select distinct genoGXD INTO TEMPORARY TABLE uniqueGXD from shareRef 
;
select distinct genoAP INTO TEMPORARY TABLE uniqueAP from shareRef
;

/* select all alleles */
select s.genoGXD, a._Allele_key_1
INTO TEMPORARY TABLE gxdAlleles
from uniqueGXD s, GXD_AllelePair a
where s.genoGXD = a._Genotype_key
union all
select s.genoGXD, a._Allele_key_2
from uniqueGXD s, GXD_AllelePair a
where s.genoGXD = a._Genotype_key
and a._Allele_key_2 is not null
;

select s.genoAP, a._Allele_key_1
INTO TEMPORARY TABLE apAlleles
from uniqueAP s, GXD_AllelePair a
where s.genoAP = a._Genotype_key
union all
select s.genoAP, a._Allele_key_2
from uniqueAP s, GXD_AllelePair a
where s.genoAP = a._Genotype_key
and a._Allele_key_2 is not null
;

/* calculate allele counts */
select s.genoGXD, count(s._Allele_key_1) as alleleCount
INTO TEMPORARY TABLE gxdCount
from gxdAlleles s
group by s.genoGXD
;

select s.genoAP, count(s._Allele_key_1) as alleleCount
INTO TEMPORARY TABLE apCount
from apAlleles s
group by s.genoAP
;

/* select those that have the same allele pair counts */
select s.*
INTO TEMPORARY TABLE sameCount
from shareRef s, gxdCount g, apcount a
where s.genoGXD = g.genoGXD
and s.genoAP = a.genoAP
and g.alleleCount = a.alleleCount
;

/* select those that do not have the same allele pairs */
/* TR 10093 */
/* should be able to remove the checks on sequenceNum */
/* however, as long as the sequenceNum are the same, the allele pair */
/* match should work correctly */
/* for now, leave the sequenceNum check in... */

select s.*
INTO TEMPORARY TABLE diffAlleles
from shareRef s, sameCount c
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
;

/* select those that have the same alleles and the same strain names */
select s.*
INTO TEMPORARY TABLE sameStrain
from sameCount s, GXD_Genotype g1, PRB_Strain s1, GXD_Genotype g2, PRB_Strain s2
where s.genoGXD = g1._Genotype_key
and s.genoAP = g2._Genotype_key
and g1._Strain_key = s1._Strain_key
and g2._Strain_key = s2._Strain_key
and s1.strain = s2.strain
and not exists (select 1 from diffAlleles a where s.genoGXD = a.genoGXD and s.genoAP = a.genoAP)
;

/* select those that have the same alleles and where there is not already */
/* another GXD/AP genotype that does match */
select a.accID as jnum, s1.strain as gxdStrain, s2.strain as apStrain, s.genoGXD
INTO TEMPORARY TABLE toPrint1
from sameCount s, GXD_Genotype g1, PRB_Strain s1, GXD_Genotype g2, PRB_Strain s2, ACC_Accession a
where s.genoGXD = g1._Genotype_key
and s.genoAP = g2._Genotype_key
and g1._Strain_key = s1._Strain_key
and g2._Strain_key = s2._Strain_key
and s1.strain != s2.strain
and not exists (select 1 from diffAlleles a where s.genoGXD = a.genoGXD and s.genoAP = a.genoAP)
and not exists (select 1 from sameStrain a where s.genoGXD = a.genoGXD and s._Refs_key = a._Refs_key)
and s._Refs_key = a._Object_key
and a._MGIType_key = 1
and a._LogicalDB_key = 1
and a.prefixPart = 'J:'
;

\echo ''
\echo 'References where GXD and Pheno differ in Genotype'
\echo ''

select substring(t.jnum,1,10) as jnum, 
substring(t.gxdStrain, 1, 75) as "GXD Strain", 
substring(t.apStrain, 1, 75) as "A&P Strain", 
substring(a1.symbol,1,30) as symbol1, 
substring(a2.symbol,1,30) as symbol2
from toPrint1 t, GXD_AllelePair a, ALL_Allele a1, ALL_Allele a2
where t.genoGXD = a._Genotype_key
and a._Allele_key_1 = a1._Allele_key
and a._Allele_key_2 = a2._Allele_key
order by t.jnum
;

