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
and symbol not like '%<+>'
union
select total = count(*), category = "transgene induced", seq = 2
from ALL_Allele
where datepart(year, creation_date) = @year
and datepart(month, creation_date) = @month
and _Allele_Type_key = 2
and symbol not like '%<+>'
union
select total = count(*), category = "transgene induced (gene targeted)", seq = 3
from ALL_Allele
where datepart(year, creation_date) = @year
and datepart(month, creation_date) = @month
and _Allele_Type_key = 3
and symbol not like '%<+>'
union
select total = count(*), category = "QTL", seq = 4
from ALL_Allele
where datepart(year, creation_date) = @year
and datepart(month, creation_date) = @month
and _Allele_Type_key = 15
and symbol not like '%<+>'
union
select total = count(*), category = "everything else", seq = 5
from ALL_Allele
where datepart(year, creation_date) = @year
and datepart(month, creation_date) = @month
and _Allele_Type_key not in (2,3,15)
and symbol not like '%<+>'

select total = count(distinct g._Genotype_key), category = "Total Genotype", seq = 1
into #c2
from GXD_Genotype g, VOC_Annot a
where a._AnnotType_key = 1001
and g._Genotype_key = a._Object_key
union
select total = count(distinct g._Genotype_key), category = "Total Genotype for Previous Month", seq = 2
from GXD_Genotype g, VOC_Annot a
where a._AnnotType_key = 1001
and datepart(year, a.creation_date) = @year
and datepart(month, a.creation_date) = @month
and g._Genotype_key = a._Object_key
union
select total = count(g._Genotype_key), category = "Total Annotations", seq = 3
from GXD_Genotype g, VOC_Annot a
where a._AnnotType_key = 1001
and g._Genotype_key = a._Object_key
union
select total = count(distinct ap._Marker_key), category = "Total Genes Annotated", seq = 4
from GXD_Genotype g, GXD_AllelePair ap, VOC_Annot a
where a._AnnotType_key = 1001
and g._Genotype_key = a._Object_key
and g._Genotype_key = ap._Genotype_key

select total = count(distinct _Allele_key), category = "Total Allele", seq = 1
into #c3
from ALL_Note
where note like "%Associated Phenotype Controlled Terms%"
union
select total = count(distinct a._Allele_key), category = "Total Allele for Previous Month", seq = 2
from ALL_Allele a, ALL_Note al
where datepart(year, a.creation_date) = @year
and datepart(month, a.creation_date) = @month
and a._Allele_key = al._Allele_key
and al.note like "%Associated Phenotype Controlled Terms%"

select total = count(*), category = "Total", seq = 1
into #c4
from ALL_Allele
where symbol not like '%<+>'
union
select total = count(*), category = "transgene induced", seq = 2
from ALL_Allele
where _Allele_Type_key = 2
and symbol not like '%<+>'
union
select total = count(*), category = "transgene induced (gene targeted)", seq = 3
from ALL_Allele
where _Allele_Type_key = 3
and symbol not like '%<+>'
union
select total = count(*), category = "QTL", seq = 4
from ALL_Allele
where _Allele_Type_key = 15
and symbol not like '%<+>'
union
select total = count(*), category = "everything else", seq = 5
from ALL_Allele
where _Allele_Type_key not in (2,3,15)
and symbol not like '%<+>'

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

