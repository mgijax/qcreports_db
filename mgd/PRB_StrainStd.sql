select s._Strain_key
INTO TEMPORARY TABLE strains1
from PRB_Strain s
where exists (select 1 from ALL_Allele a where s._Strain_key = a._Strain_key)
;

INSERT INTO strains1
select s._Strain_key
from PRB_Strain s
where exists (select 1 from ALL_CellLine a where s._Strain_key = a._Strain_key)
;

INSERT INTO strains1
select s._Strain_key
from PRB_Strain s
where exists (select 1 from GXD_Genotype a where s._Strain_key = a._Strain_key)
;

INSERT INTO strains1
select s._Strain_key
from PRB_Strain s
where exists (select 1 from MLD_Fish a where s._Strain_key = a._Strain_key)
;

INSERT INTO strains1
select s._Strain_key
from PRB_Strain s
where exists (select 1 from PRB_Source a where s._Strain_key = a._Strain_key)
;

INSERT INTO strains1
select s._Strain_key
from PRB_Strain s
where exists (select 1 from CRS_Cross a where s._Strain_key = a._femaleStrain_key)
;

INSERT INTO strains1
select s._Strain_key
from PRB_Strain s
where exists (select 1 from CRS_Cross a where s._Strain_key = a._maleStrain_key)
;

INSERT INTO strains1
select s._Strain_key
from PRB_Strain s
where exists (select 1 from RI_RISet a where s._Strain_key = a._Strain_key_1)
;

INSERT INTO strains1
select s._Strain_key
from PRB_Strain s
where exists (select 1 from RI_RISet a where s._Strain_key = a._Strain_key_2)
;

create index idx1 on strains1(_Strain_key)
;

select s._Strain_key, a.accID as mgiID, 'y'::text as dataExists
INTO TEMPORARY TABLE strains2
from PRB_Strain s, ACC_Accession a
where s.standard = 1
and s._Strain_key = a._Object_key
and a._MGIType_key = 10
and a._LogicalDB_key = 1
and a.preferred = 1
and exists (select 1 from strains1 ss where ss._Strain_key = s._Strain_key)
;

INSERT INTO strains2
select s._Strain_key, a.accID as mgiID, 'n'::text as dataExists
from PRB_Strain s, ACC_Accession a
where s.standard = 1
and s._Strain_key = a._Object_key
and a._MGIType_key = 10
and a._LogicalDB_key = 1
and a.preferred = 1
and not exists (select 1 from strains1 ss where ss._Strain_key = s._Strain_key)
;

create unique index idx2 on strains2(_Strain_key)
;

\echo ''
\echo 'Standard Strains'
\echo ''

select n.dataExists as "data attached", substring(l.name,1,20) as "external db", 
a.accID as "external id", n.mgiID as "MGI id", substring(s.strain,1,80) as "strain"
from PRB_Strain s, ACC_Accession a, ACC_LogicalDB l, strains2 n
where s.standard = 1
and s._Strain_key = n._Strain_key
and a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key != 1
and a._LogicalDB_key = l._LogicalDB_key
union
select n.dataExists as "data attached", null, null, n.mgiID as "MGI id", 
substring(s.strain,1,80) as "strain"
from PRB_Strain s, strains2 n
where s.standard = 1
and s._Strain_key = n._Strain_key
and not exists (select 1 from ACC_Accession a
where a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key != 1)
order by strain
;

