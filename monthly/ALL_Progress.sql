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

select total = count(distinct al._Allele_key), category = "Total Allele"
into #c3
from GXD_Genotype g, GXD_AllelePair ap, ALL_Note al
where g._Genotype_key = ap._Genotype_key
and ap._Allele_key_1 = al._Allele_key
and ap._Allele_key_2 is null
and al.note like "%Associated Phenotype Controlled Terms%"
union
select total = count(distinct al1._Allele_key) + count(distinct al2._Allele_key), category = "Total Allele"
from GXD_Genotype g, GXD_AllelePair ap, ALL_Note al1, ALL_Note al2
where g._Genotype_key = ap._Genotype_key
and ap._Allele_key_1 != ap._Allele_key_2
and ap._Allele_key_1 = al1._Allele_key
and ap._Allele_key_2 = al2._Allele_key
and (al1.note like "%Associated Phenotype Controlled Terms%"
or al2.note like "%Associated Phenotype Controlled Terms%")
union
select total = count(distinct al._Allele_key), category = "Total Allele for Previous Month"
from GXD_Genotype g, GXD_AllelePair ap, ALL_Note al
where datepart(year, g.creation_date) = @year
and datepart(month, g.creation_date) = @month
and g._Genotype_key = ap._Genotype_key
and ap._Allele_key_1 = al._Allele_key
and ap._Allele_key_2 is null
and al.note like "%Associated Phenotype Controlled Terms%"
union
select total = count(distinct al1._Allele_key) + count(distinct al2._Allele_key), category = "Total Allele for Previous Month"
from GXD_Genotype g, GXD_AllelePair ap, ALL_Note al1, ALL_Note al2
where datepart(year, g.creation_date) = @year
and datepart(month, g.creation_date) = @month
and g._Genotype_key = ap._Genotype_key
and ap._Allele_key_1 != ap._Allele_key_2
and ap._Allele_key_1 = al1._Allele_key
and ap._Allele_key_2 = al2._Allele_key
and (al1.note like "%Associated Phenotype Controlled Terms%"
or al2.note like "%Associated Phenotype Controlled Terms%")

set nocount off

print ""
print "New Alleles Entered in Previous Month (excluding wild types)"
print ""

select category, total from #c1 order by seq
go

print ""
print "Genotypes Associated with at least one Phenotype Term"
print ""

select category, total from #c2 order by seq
go

print ""
print "Alleles with 'Associated Phenotype Controlled Terms' in Notes"
print ""

select category, sum(total) from #c3 group by category
go

