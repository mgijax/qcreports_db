select s._Strain_key, 'y'::text as dataExists
INTO TEMPORARY TABLE strains
from PRB_Strain s
where s.standard = 0
and s.strain not like '%)F1%'
and s.strain not like '%)F2%'
;

create unique index index_strain_key1 on strains(_Strain_key)
;

select s._Strain_key
INTO TEMPORARY TABLE toUpdate
from strains s
where
not exists (select 1 from ALL_Allele a where s._Strain_key = a._Strain_key)
and not exists (select 1 from ALL_CellLine a where s._Strain_key = a._Strain_key)
and not exists (select 1 from GXD_Genotype a where s._Strain_key = a._Strain_key)
and not exists (select 1 from MLD_Fish a where s._Strain_key = a._Strain_key)
and not exists (select 1 from PRB_Source a where s._Strain_key = a._Strain_key)
and not exists (select 1 from CRS_Cross a where s._Strain_key = a._femaleStrain_key)
and not exists (select 1 from CRS_Cross a where s._Strain_key = a._maleStrain_key)
and not exists (select 1 from RI_RISet a where s._Strain_key = a._Strain_key_1)
and not exists (select 1 from RI_RISet a where s._Strain_key = a._Strain_key_2)
;

create unique index index_strain_key2 on toUpdate(_Strain_key)
;

update strains 
set dataExists = 'n'
from toUpdate u, strains s
where u._Strain_key = s._Strain_key
;

\echo ''
\echo 'Non Standard Strains (excluding F1 and F2): data attached = yes'
\echo ''

select substring(l.name,1,20) as "external db", a.accID as "external id", 
substring(s.strain,1,125) as "strain"
from PRB_Strain s, ACC_Accession a, ACC_LogicalDB l, strains n
where s.standard = 0
and s.strain not like '%)F1%'
and s.strain not like '%)F2%'
and s._Strain_key = n._Strain_key
and n.dataExists = 'y'
and a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key != 1
and a._LogicalDB_key = l._LogicalDB_key
union
select null, null,substring(s.strain,1,125)
from PRB_Strain s, strains n
where s.standard = 0
and s.strain not like '%)F1%'
and s.strain not like '%)F2%'
and s._Strain_key = n._Strain_key
and n.dataExists = 'y'
and not exists (select 1 from ACC_Accession a
where a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key != 1)
order by strain
;

\echo ''
\echo 'Non Standard Strains (excluding F1 and F2): data attached = no'
\echo ''

select substring(l.name,1,20) as "external db", a.accID as "external id", 
substring(s.strain,1,125) as "strain"
from PRB_Strain s, ACC_Accession a, ACC_LogicalDB l, strains n
where s.standard = 0
and s.strain not like '%)F1%'
and s.strain not like '%)F2%'
and s._Strain_key = n._Strain_key
and n.dataExists = 'n'
and a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key != 1
and a._LogicalDB_key = l._LogicalDB_key
union
select null, null, substring(s.strain,1,125) as "strain"
from PRB_Strain s, strains n
where s.standard = 0
and s.strain not like '%)F1%'
and s.strain not like '%)F2%'
and s._Strain_key = n._Strain_key
and n.dataExists = 'n'
and not exists (select 1 from ACC_Accession a
where a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key != 1)
order by strain
;

