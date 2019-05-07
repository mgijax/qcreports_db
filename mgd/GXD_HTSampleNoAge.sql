\echo ''
\echo 'Sample with Not Applicable, Not Specified'
\echo 'Relevance = Yes'
\echo ''

select a1.accID as exptID, s.name
from GXD_HTSample s, ACC_Accession a1
where s._Relevance_key = 20475450
and (s.age like 'Not Applicable%' or s.age like 'Not Specified%')
and s._Sample_key = a1._Object_key
and a1._MGIType_key = 42
and a1._LogicalDB_key = 189
;

\echo ''
\echo 'Postnatal Age annotated to embryonic structures'
\echo 'Relevance = Yes'
\echo ''

select a1.accID as exptID, s.name
from GXD_HTSample s, GXD_TheilerStage t, ACC_Accession a1
where s._Relevance_key = 20475450
and s.age like 'postnatal%'
and s._Stage_key = t._Stage_key
and t.stage not in (27, 28)
and s._Sample_key = a1._Object_key
and a1._MGIType_key = 42
and a1._LogicalDB_key = 189
;

\echo ''
\echo 'Age either ''postnatal'', ''postnatal adult'', ''postnatal newborn'' but age range entered'
\echo 'Relevance = Yes'
\echo ''

select s.age, a1.accID as exptID, s.name
from GXD_HTSample s, ACC_Accession a1
where s._Relevance_key = 20475450
and
(
s.age ~ 'postnatal [0-9]'
or
s.age ~ 'postnatal adult [0-9]'
or
s.age ~ 'postnatal newborn [0-9]'
)
and s._Sample_key = a1._Object_key
and a1._MGIType_key = 42
and a1._LogicalDB_key = 189
;

\echo ''
\echo 'postnatal age in (''day 0'', ''day 0.5'', ''day 1'', ''day 1.5'', ''day 2'', ''day 2.5'', ''day 3'', ''day 3.5'', ''newborn''), but not TS27'
\echo 'Relevance = Yes'
\echo ''

select s.age, a1.accID as exptID, s.name
from GXD_HTSample s, GXD_TheilerStage t, ACC_Accession a1
where s._Relevance_key = 20475450
and s._Stage_key = t._Stage_key
and t.stage not in (27)
and
(
s.age = 'postnatal day 0' or
s.age = 'postnatal day 0.5' or
s.age = 'postnatal day 1' or
s.age = 'postnatal day 1.5' or
s.age = 'postnatal day 2' or
s.age = 'postnatal day 2.5' or
s.age = 'postnatal day 3' or
s.age = 'postnatal day 3.5' or
s.age like 'postnatal newborn%'
)
and s._Sample_key = a1._Object_key
and a1._MGIType_key = 42
and a1._LogicalDB_key = 189
;

\echo ''
\echo 'Theiler = 28 and ageMin < 21.01'
\echo 'Relevance = Yes'
\echo 'excludes placenta,decidua,decidua basalis,decidua capsularis, cumulus oophorus, uterus'
\echo ''

select s.age, s.ageMin, a1.accID as exptID, s.name
from GXD_HTSample s, GXD_TheilerStage t, VOC_Term vt, ACC_Accession a1
where s._Relevance_key = 20475450
and s._Stage_key = t._Stage_key
and t.stage = 28
and s.ageMin < 21.01
and s._emapa_key = vt._Term_key
and vt.term not in ('placenta','decidua','decidua basalis','decidua capsularis','cumulus oophorus','uterus')
and s._Sample_key = a1._Object_key
and a1._MGIType_key = 42
and a1._LogicalDB_key = 189
;

\echo ''
\echo 'Theiler = 27 and ageMin < 21.01' or ageMin not > 28.01
\echo 'Relevance = Yes'
\echo 'excludes (placenta,decidua,decidua basalis,decidua capsularis, cumulus oophorus'
\echo ''

select s.age, s.ageMin, a1.accID as exptID, s.name
from GXD_HTSample s, GXD_TheilerStage t, VOC_Term vt, ACC_Accession a1
where s._Relevance_key = 20475450
and s._Stage_key = t._Stage_key
and t.stage = 27
and (s.ageMin < 21.01 or s.ageMax > 28.01)
and s._emapa_key = vt._Term_key
and vt.term not in ('placenta','decidua','decidua basalis','decidua capsularis','cumulus oophorus')
and s._Sample_key = a1._Object_key
and a1._MGIType_key = 42
and a1._LogicalDB_key = 189
;

