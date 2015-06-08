set nocount on
go

select s._Strain_key
into #strains1
from PRB_Strain s
where exists (select 1 from ALL_Allele a where s._Strain_key = a._Strain_key)
go

insert into #strains1
select s._Strain_key
from PRB_Strain s
where exists (select 1 from ALL_CellLine a where s._Strain_key = a._Strain_key)
go

insert into #strains1
select s._Strain_key
from PRB_Strain s
where exists (select 1 from GXD_Genotype a where s._Strain_key = a._Strain_key)
go

insert into #strains1
select s._Strain_key
from PRB_Strain s
where exists (select 1 from MLD_Fish a where s._Strain_key = a._Strain_key)
go

insert into #strains1
select s._Strain_key
from PRB_Strain s
where exists (select 1 from PRB_Source a where s._Strain_key = a._Strain_key)
go

insert into #strains1
select s._Strain_key
from PRB_Strain s
where exists (select 1 from CRS_Cross a where s._Strain_key = a._femaleStrain_key)
go

insert into #strains1
select s._Strain_key
from PRB_Strain s
where exists (select 1 from CRS_Cross a where s._Strain_key = a._maleStrain_key)
go

insert into #strains1
select s._Strain_key
from PRB_Strain s
where exists (select 1 from RI_RISet a where s._Strain_key = a._Strain_key_1)
go

insert into #strains1
select s._Strain_key
from PRB_Strain s
where exists (select 1 from RI_RISet a where s._Strain_key = a._Strain_key_2)
go

create index idx1 on #strains1(_Strain_key)
go

select s._Strain_key, a.accID as mgiID, 'y' as dataExists
into #strains2
from PRB_Strain s, ACC_Accession a
where s.standard = 1
and s._Strain_key = a._Object_key
and a._MGIType_key = 10
and a._LogicalDB_key = 1
and a.preferred = 1
and exists (select 1 from #strains1 ss where ss._Strain_key = s._Strain_key)
go

insert into #strains2
select s._Strain_key, a.accID as mgiID, 'n' as dataExists
from PRB_Strain s, ACC_Accession a
where s.standard = 1
and s._Strain_key = a._Object_key
and a._MGIType_key = 10
and a._LogicalDB_key = 1
and a.preferred = 1
and not exists (select 1 from #strains1 ss where ss._Strain_key = s._Strain_key)
go

create unique index idx2 on #strains2(_Strain_key)
go

set nocount off
go

print ''
print 'Standard Strains'
print ''

select n.dataExists as "data attached", substring(l.name,1,20) as "external db", 
a.accID as "external id", n.mgiID as "MGI id", substring(s.strain,1,80) as "strain"
from PRB_Strain s, ACC_Accession a, ACC_LogicalDB l, #strains2 n
where s.standard = 1
and s._Strain_key = n._Strain_key
and a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key != 1
and a._LogicalDB_key = l._LogicalDB_key
union
select n.dataExists as "data attached", null, null, n.mgiID as "MGI id", 
substring(s.strain,1,80) as "strain"
from PRB_Strain s, #strains2 n
where s.standard = 1
and s._Strain_key = n._Strain_key
and not exists (select 1 from ACC_Accession a
where a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key != 1)
order by strain
go

