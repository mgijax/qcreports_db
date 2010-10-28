
print ""
print "Hemizygous Genotype Check"
print ""

set nocount on
go

/* genotypes that have 2 alleles and pair state = heterozygous or homozygous and chromosome is X or Y */

select g._Genotype_key, a.name
into #genotypes
from GXD_AllelePair g, ALL_Allele a, MRK_Marker m
where g._PairState_key in (847137, 847138)
and g._Allele_key_2 is not null
and g._Allele_key_1 = a._Allele_key
and a._Marker_key = m._Marker_key
and m.chromosome in ("X","Y")
go

create index idx1 on #genotypes(_Genotype_key)
go

set nocount off
go

print ""
print "specimens"
print "genotypes that have 2 alleles and pair state = heterozygous or homozygous"
print "mutated gene on X or Y"
print "sex = male"
print ""

select distinct a1.accID "J number of assay", a2.accID "MGI ID of assay", substring(g.name, 1, 30) "name of allele1 of genotype"
from #genotypes g, GXD_Assay a, GXD_Specimen s, ACC_Accession a1, ACC_Accession a2
where g._Genotype_key = s._Genotype_key
and s.sex = 'Male'
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
and a._Refs_key = a1._Object_key
and a1._MGIType_key = 1
and a1.prefixPart = "J:"
and s._Assay_key = a2._Object_key
and a2._MGIType_key = 8
order by a1.numericPart
go

print ""
print "gels"
print "genotypes that have 2 alleles and pair state = heterozygous or homozygous"
print "mutated gene on X or Y"
print "sex = male"
print ""

select distinct a1.accID "J number of assay", a2.accID "MGI ID of assay", substring(g.name, 1, 30) "name of allele1 of genotype"
from #genotypes g, GXD_Assay a, GXD_GelLane s, ACC_Accession a1, ACC_Accession a2
where g._Genotype_key = s._Genotype_key
and s.sex = 'Male'
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
and a._Refs_key = a1._Object_key
and a1._MGIType_key = 1
and a1.prefixPart = "J:"
and s._Assay_key = a2._Object_key
and a2._MGIType_key = 8
order by a1.numericPart
go

