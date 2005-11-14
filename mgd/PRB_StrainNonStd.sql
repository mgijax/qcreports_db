set nocount on
go

select s._Strain_key, dataExists = "y"
into #strains
from PRB_Strain s
where 1 = 2
go

insert into #strains
select s._Strain_key, dataExists = "y"
from PRB_Strain s
where s.standard = 0
and s.strain not like '%)F1%'
and s.strain not like '%)F2%'
and 
(
exists (select 1 from ALL_Allele a where s._Strain_key = a._Strain_key)
or exists (select 1 from ALL_CellLine a where s._Strain_key = a._Strain_key)
or exists (select 1 from GXD_Genotype a where s._Strain_key = a._Strain_key)
or exists (select 1 from MLD_Fish a where s._Strain_key = a._Strain_key)
or exists (select 1 from PRB_Allele_Strain a where s._Strain_key = a._Strain_key)
or exists (select 1 from PRB_Source a where s._Strain_key = a._Strain_key)
or exists (select 1 from CRS_Cross a where s._Strain_key = a._femaleStrain_key)
or exists (select 1 from CRS_Cross a where s._Strain_key = a._maleStrain_key)
or exists (select 1 from RI_RISet a where s._Strain_key = a._Strain_key_1)
or exists (select 1 from RI_RISet a where s._Strain_key = a._Strain_key_2)
)
union
select s._Strain_key, dataExists = "n"
from PRB_Strain s
where s.standard = 0
and s.strain not like '%)F1%'
and s.strain not like '%)F2%'
and not exists (select 1 from ALL_Allele a where s._Strain_key = a._Strain_key)
and not exists (select 1 from ALL_CellLine a where s._Strain_key = a._Strain_key)
and not exists (select 1 from GXD_Genotype a where s._Strain_key = a._Strain_key)
and not exists (select 1 from MLD_Fish a where s._Strain_key = a._Strain_key)
and not exists (select 1 from PRB_Allele_Strain a where s._Strain_key = a._Strain_key)
and not exists (select 1 from PRB_Source a where s._Strain_key = a._Strain_key)
and not exists (select 1 from CRS_Cross a where s._Strain_key = a._femaleStrain_key)
and not exists (select 1 from CRS_Cross a where s._Strain_key = a._maleStrain_key)
and not exists (select 1 from RI_RISet a where s._Strain_key = a._Strain_key_1)
and not exists (select 1 from RI_RISet a where s._Strain_key = a._Strain_key_2)
go

create unique index index_strain_key on #strains(_Strain_key)
go

set nocount off
go

print ""
print "Non Standard Strains (excluding F1 and F2): data attached = yes"
print ""

select a.accID "external id", substring(s.strain,1,125) "strain"
from PRB_Strain s, ACC_Accession a, #strains n
where s.standard = 0
and s.strain not like '%)F1%'
and s.strain not like '%)F2%'
and s._Strain_key = n._Strain_key
and n.dataExists = 'y'
and a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key != 1
union
select null, substring(s.strain,1,125)
from PRB_Strain s, #strains n
where s.standard = 0
and s.strain not like '%)F1%'
and s.strain not like '%)F2%'
and s._Strain_key = n._Strain_key
and n.dataExists = 'y'
and not exists (select 1 from ACC_Accession a
where a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key != 1)
order by s.strain
go

print ""
print "Non Standard Strains (excluding F1 and F2): data attached = no"
print ""

select a.accID "external id", substring(s.strain,1,125) "strain"
from PRB_Strain s, ACC_Accession a, #strains n
where s.standard = 0
and s.strain not like '%)F1%'
and s.strain not like '%)F2%'
and s._Strain_key = n._Strain_key
and n.dataExists = 'n'
and a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key != 1
union
select null, substring(s.strain,1,125)
from PRB_Strain s, #strains n
where s.standard = 0
and s.strain not like '%)F1%'
and s.strain not like '%)F2%'
and s._Strain_key = n._Strain_key
and n.dataExists = 'n'
and not exists (select 1 from ACC_Accession a
where a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key != 1)
order by s.strain
go

