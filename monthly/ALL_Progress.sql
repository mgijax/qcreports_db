set nocount on
go

declare @year integer
select @year = datepart(year, getdate())
declare @month integer
select @month = datepart(month, getdate())

if @month = 1
begin
	select @month = 12
	select @year = @year - 1
end
else
begin
	select @month = @month - 1
end

select total = count(*), category = "Total", seq = 1
into #c1
from ALL_Allele
where datepart(year, creation_date) = @year
and datepart(month, creation_date) = @month
and isWildType = 0
union
select total = count(a._Allele_key), category = "transgenic (all types)", seq = 2
from ALL_Allele a, VOC_Term t
where datepart(year, a.creation_date) = @year
and datepart(month, a.creation_date) = @month
and a._Allele_Type_key = t._Term_key
and t.term like 'Transgenic%'
and a.isWildType = 0
union
select total = count(a._Allele_key), category = "targeted (all types)", seq = 3
from ALL_Allele a, VOC_Term t
where datepart(year, a.creation_date) = @year
and datepart(month, a.creation_date) = @month
and a._Allele_Type_key = t._Term_key
and t.term like 'Targeted%'
and a.isWildType = 0
union
select total = count(a._Allele_key), category = "QTL", seq = 4
from ALL_Allele a, VOC_Term t
where datepart(year, a.creation_date) = @year
and datepart(month, a.creation_date) = @month
and a._Allele_Type_key = t._Term_key
and t.term = 'QTL'
and a.isWildType = 0
union
select total = count(a._Allele_key), category = "everything else", seq = 5
from ALL_Allele a, VOC_Term t
where datepart(year, a.creation_date) = @year
and datepart(month, a.creation_date) = @month
and a._Allele_Type_key = t._Term_key
and t.term not like 'Transgenic%'
and t.term not like 'Targeted%'
and t.term != 'QTL'
and a.isWildType = 0

select total = count(distinct g._Genotype_key), category = "Total Genotype", seq = 1
into #c2
from GXD_Genotype g, VOC_Annot a
where a._AnnotType_key = 1002
and g._Genotype_key = a._Object_key
union
select total = count(distinct g._Genotype_key), category = "Total Genotype for Previous Month", seq = 2
from GXD_Genotype g, VOC_Annot a
where a._AnnotType_key = 1002
and datepart(year, a.creation_date) = @year
and datepart(month, a.creation_date) = @month
and g._Genotype_key = a._Object_key
union
select total = count(g._Genotype_key), category = "Total Annotations", seq = 3
from GXD_Genotype g, VOC_Annot a
where a._AnnotType_key = 1002
and g._Genotype_key = a._Object_key
union
select total = count(distinct ap._Marker_key), category = "Total Genes Annotated", seq = 4
from GXD_Genotype g, GXD_AllelePair ap, VOC_Annot a
where a._AnnotType_key = 1002
and g._Genotype_key = a._Object_key
and g._Genotype_key = ap._Genotype_key

select total = count(distinct n._Object_key), category = "Total Allele", seq = 1
into #c3
from MGI_Note n, MGI_NoteChunk nc
where n._MGIType_key = 11
and n._Note_key = nc._Note_key
and nc.note like "%Associated Phenotype Controlled Terms%"
union
select total = count(distinct n._Object_key), category = "Total Allele for Previous Month", seq = 2
from MGI_Note n, MGI_NoteChunk nc
where n._MGIType_key = 11
and n._Note_key = nc._Note_key
and datepart(year, n.creation_date) = @year
and datepart(month, n.creation_date) = @month
and nc.note like "%Associated Phenotype Controlled Terms%"

select total = count(*), category = "Total", seq = 1
into #c4
from ALL_Allele
where isWildType = 0
union
select total = count(a._Allele_key), category = "transgenic (all types)", seq = 2
from ALL_Allele a, VOC_Term t
where a._Allele_Type_key = t._Term_key
and t.term like 'Transgenic%'
and a.isWildType = 0
union
select total = count(a._Allele_key), category = "targeted (all types)", seq = 3
from ALL_Allele a, VOC_Term t
where a._Allele_Type_key = t._Term_key
and t.term like 'Targeted%'
and a.isWildType = 0
union
select total = count(a._Allele_key), category = "QTL", seq = 4
from ALL_Allele a, VOC_Term t
where a._Allele_Type_key = t._Term_key
and t.term = 'QTL'
and a.isWildType = 0
union
select total = count(a._Allele_key), category = "everything else", seq = 5
from ALL_Allele a, VOC_Term t
where a._Allele_Type_key = t._Term_key
and t.term not like 'Transgenic%'
and t.term not like 'Targeted%'
and t.term != 'QTL'
and a.isWildType = 0

select total = count(distinct a._Marker_key), category = "Total", seq = 1
into #c5
from ALL_Allele a, MRK_Marker m
where a.isWildType = 0
and a._Marker_key = m._Marker_key
and m._Marker_Type_key = 1
union
select total = count(distinct a._Marker_key), cagegory = "genes w/ targeted (all types)", seq = 2
from ALL_Allele a, MRK_Marker m, VOC_Term t
where a._Allele_Type_key = t._Term_key
and t.term like 'Targeted%'
and a._Marker_key = m._Marker_key
and m._Marker_Type_key = 1
union
select total = count(distinct a._Marker_key), category = "genes w/ gene trapped", seq = 3
from ALL_Allele a, MRK_Marker m, VOC_Term t
where a._Allele_Type_key = t._Term_key
and t.term = 'Gene trapped'
and a._Marker_key = m._Marker_key
and m._Marker_Type_key = 1
union
select total = count(distinct m._Marker_key), category = "genes w/ both (targeted) & (gene trapped)", seq = 4
from ALL_Allele a1, ALL_Allele a2, MRK_Marker m, VOC_Term t1, VOC_Term t2
where a1._Allele_Type_key = t1._Term_key
and t1.term like 'Targeted%'
and a1._Marker_key = m._Marker_key
and a2._Allele_Type_key = t2._Term_key
and t2.term = 'Gene trapped'
and a2._Marker_key = m._Marker_key
and a1._Marker_key = a2._Marker_key
and m._Marker_Type_key = 1

set nocount off

print ""
print "For Month %1!/%2!", @month, @year
print ""

print ""
print "Current State (excluding wild types)"
print ""

select category, total from #c4 order by seq

print ""
print "New Alleles Entered in Previous Month (excluding wild types)"
print ""

select category, total from #c1 order by seq

print ""
print "Genotypes Associated with at least one Phenotype Term"
print ""

select category, total from #c2 order by seq

print ""
print "Alleles with 'Associated Phenotype Controlled Terms' in Notes"
print ""

select category, total from #c3 order by seq
go

print ""
print "Number of Genes with Alleles (excluding wild types)"
print ""

select category, total from #c5 order by seq
go

