select s._Assay_key, substring(s.specimenLabel, 1, 50) as specimenLabel
INTO TEMPORARY TABLE spec1
from GXD_Specimen s
where (s.age like 'Not Applicable%' or s.age like 'Not Specified%')
;

select s._Assay_key, substring(s.laneLabel, 1, 50) as laneLabel
INTO TEMPORARY TABLE spec2
from GXD_GelLane s, VOC_Term t
where s._GelControl_key = t._Term_key and t.term = 'No'
and (s.age like 'Not Applicable%' or s.age like 'Not Specified%')
;

create index spec1_idx1 on spec1(_Assay_key)
;
create index spec2_idx1 on spec2(_Assay_key)
;

\echo ''
\echo 'InSitu Specimens with Not Applicable, Not Specified'
\echo ''

select a1.accID as mgiID, a2.accID as jnumID, s.specimenLabel, u.login
from spec1 s, GXD_Assay ga, ACC_Accession a1, ACC_Accession a2, MGI_User u
where s._Assay_key = ga._Assay_key
and ga._AssayType_key in (1,2,3,4,5,6,8,9)
and ga._Assay_key = a1._Object_key
and a1._MGIType_key = 8
and a1._LogicalDB_key = 1
and a1.prefixPart = 'MGI:'
and a1.preferred = 1
and ga._Refs_key = a2._Object_key
and a2._MGIType_key = 1
and a2._LogicalDB_key = 1
and a2.prefixPart = 'J:'
and a2.preferred = 1
and ga._Modifiedby_key = u._User_key
;

\echo ''
\echo 'Gel Lane Specimens with Not Applicable, Not Specified'
\echo ''

select a1.accID as mgiID, a2.accID as jnumID, s.laneLabel, u.login
from spec2 s, GXD_Assay ga, ACC_Accession a1, ACC_Accession a2, MGI_User u
where s._Assay_key = ga._Assay_key
and ga._AssayType_key in (1,2,3,4,5,6,8,9)
and ga._Assay_key = a1._Object_key
and a1._MGIType_key = 8
and a1._LogicalDB_key = 1
and a1.prefixPart = 'MGI:'
and a1.preferred = 1
and ga._Refs_key = a2._Object_key
and a2._MGIType_key = 1
and a2._LogicalDB_key = 1
and a2.prefixPart = 'J:'
and a2.preferred = 1
and ga._Modifiedby_key = u._User_key
;

select distinct s._Specimen_key
INTO TEMPORARY TABLE temp1
from GXD_Specimen s, GXD_InSituResult i, GXD_ISResultStructure r, GXD_TheilerStage t
where s.age like 'postnatal%'
and s._Specimen_key = i._Specimen_key
and i._Result_key = r._Result_key
and r._Stage_key = t._Stage_key
and t.stage not in (27, 28)
;

select distinct i._GelLane_key
INTO TEMPORARY TABLE temp2
from GXD_GelLane i, GXD_GelLaneStructure r, GXD_TheilerStage t
where i.age like 'postnatal%'
and i._GelLane_key = r._GelLane_key
and r._Stage_key = t._Stage_key
and t.stage not in (27, 28)
;

\echo ''
\echo 'Postnatal Age InSitu Specimens annotated to embryonic structures'
\echo ''

select a.mgiID, a.jnumID, substring(s.specimenLabel, 1, 50) as specimenLabel, a.modifiedby
from temp1 t, GXD_Specimen s, GXD_Assay_View a
where t._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
;

\echo ''
\echo 'Postnatal Age Gel Lanes annotated to embryonic structures'
\echo ''

select a.mgiID, a.jnumID, substring(s.laneLabel, 1, 50) as laneLabel, a.modifiedby
from temp2 t, GXD_GelLane s, GXD_Assay_View a
where t._GelLane_key = s._GelLane_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
;

\echo ''
\echo 'InSitu Specimens with Age either ''postnatal'', ''postnatal adult'', ''postnatal newborn'' but age range entered'
\echo ''

select s.age, a.mgiID, a.jnumID, substring(s.specimenLabel, 1, 50) as specimenLabel, a.modifiedby
from GXD_Specimen s, GXD_Assay_View a
where
(
s.age ~ 'postnatal [0-9]'
or
s.age ~ 'postnatal adult [0-9]'
or
s.age ~ 'postnatal newborn [0-9]'
)
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
;

\echo ''
\echo 'Gel Lane Specimens with Age either ''postnatal'', ''postnatal adult'', ''postnatal newborn'' but age range entered'
\echo ''

select s.age, a.mgiID, a.jnumID, substring(s.laneLabel, 1, 50) as laneLabel, a.modifiedby
from GXD_GelLane s, GXD_Assay_View a
where
(
s.age ~ 'postnatal [0-9]'
or
s.age ~ 'postnatal adult [0-9]'
or
s.age ~ 'postnatal newborn [0-9]'
)
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
;

\echo ''
\echo 'In Situ Specimens with postnatal in (agemin >=21.01 AND agemax <=25.00), but not TS27'
\echo ''

select distinct s._Specimen_key
INTO TEMPORARY TABLE temp3
from GXD_Specimen s, GXD_InSituResult i, GXD_ISResultStructure r, GXD_TheilerStage t
where s._Specimen_key = i._Specimen_key
and i._Result_key = r._Result_key
and r._Stage_key = t._Stage_key
and t.stage = 27
;

create index temp3_idx on temp3(_Specimen_key )
;

select s.age, a.mgiID, a.jnumID, substring(s.specimenLabel, 1, 50) as specimenLabel, a.modifiedby
from GXD_Specimen s, GXD_Assay_View a
where s.age like 'postnatal%'
and (s.ageMin >= 21.01 and s.ageMax < 25.00)
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
and not exists (select 1 from temp3 t
where s._Specimen_key = t._Specimen_key)
;

\echo ''
\echo 'Gel Lane Specimens with postnatal in (agemin >=21.01 AND agemax <=25.00), but not TS27'
\echo ''

select distinct i._GelLane_key
INTO TEMPORARY TABLE temp4
from GXD_GelLane i, GXD_GelLaneStructure r, GXD_TheilerStage t, VOC_Term tt
where i._GelControl_key = tt._Term_key and tt.term = 'No'
and i._GelLane_key = r._GelLane_key
and r._Stage_key = t._Stage_key
and t.stage = 27
;

create index temp4_idx on temp4(_GelLane_key )
;

select s.age, a.mgiID, a.jnumID, substring(s.laneLabel, 1, 50) as laneLabel, a.modifiedby
from GXD_GelLane s, GXD_Assay_View a, VOC_Term t
where s.age like 'postnatal%'
and (s.ageMin >= 21.01 and s.ageMax < 25.00)
and s._GelControl_key = t._Term_key and t.term = 'No'
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
and not exists (select 1 from temp4 t
where s._GelLane_key = t._GelLane_key)
;

\echo ''
\echo 'InSitu Specimens where Theiler = 28 and ageMin < 21.01'
\echo 'excludes placenta,decidua,decidua basalis,decidua capsularis, cumulus oophorus, uterus'
\echo ''

select gs.age, gs.ageMin, a1.accID as mgiid, gs.specimenLabel, u.login
from GXD_Assay ga, GXD_Specimen gs, GXD_InSituResult i, GXD_ISResultStructure r, VOC_Term s, GXD_TheilerStage t, ACC_Accession a1, MGI_User u
where ga._AssayType_key in (1,2,3,4,5,6,8,9)
and ga._Assay_key = gs._Assay_key
and gs.ageMin < 21.01
and gs._Specimen_key = i._Specimen_key
and i._Result_key = r._Result_key
and r._Stage_key = t._Stage_key
and r._EMAPA_Term_key = s._Term_key
and s.term not in ('placenta','decidua','decidua basalis','decidua capsularis', 'cumulus oophorus', 'uterus')
and t.stage = 28 
and gs._Assay_key = a1._Object_key
and a1._MGIType_key = 8
and a1._LogicalDB_key = 1
and a1.prefixPart = 'MGI:'
and ga._Modifiedby_key = u._User_key
;

\echo ''
\echo 'InSitu Specimens where Theiler = 27 and ageMin < 21.01' or ageMin not > 28.01
\echo 'excludes (placenta,decidua,decidua basalis,decidua capsularis, cumulus oophorus'
\echo ''

select gs.age, gs.ageMin, gs.ageMax, a1.accID as mgiid, gs.specimenLabel, u.login
from GXD_Assay ga, GXD_Specimen gs, GXD_InSituResult i, GXD_ISResultStructure r, VOC_Term s, GXD_TheilerStage t, ACC_Accession a1, MGI_User u
where ga._AssayType_key in (1,2,3,4,5,6,8,9)
and ga._Assay_key = gs._Assay_key
and (gs.ageMin < 21.01 or gs.ageMax > 28.01)
and gs._Specimen_key = i._Specimen_key
and i._Result_key = r._Result_key
and r._Stage_key = t._Stage_key
and r._EMAPA_Term_key = s._Term_key
and s.term not in ('placenta','decidua','decidua basalis','decidua capsularis', 'cumulus oophorus')
and t.stage = 27
and gs._Assay_key = a1._Object_key
and a1._MGIType_key = 8
and a1._LogicalDB_key = 1
and a1.prefixPart = 'MGI:'
and ga._Modifiedby_key = u._User_key
;

\echo ''
\echo 'Gel Lanes where Theiler = 28 and ageMin < 21.01'
\echo 'excludes placenta,decidua,decidua basalis,decidua capsularis, cumulus oophorus, uterus'
\echo ''

select gs.age, gs.ageMin, a1.accID as mgiid, gs.laneLabel, u.login
from GXD_Assay ga, GXD_GelLane gs, GXD_GelLaneStructure r, VOC_Term s, GXD_TheilerStage t, ACC_Accession a1, VOC_Term tt, MGI_User u
where ga._AssayType_key in (1,2,3,4,5,6,8,9)
and ga._Assay_key = gs._Assay_key
and gs._GelControl_key = tt._Term_key and tt.term = 'No'
and gs.ageMin < 21.01
and gs._GelLane_key = r._GelLane_key
and r._Stage_key = t._Stage_key
and r._EMAPA_Term_key = s._Term_key
and s.term not in ('placenta','decidua','decidua basalis','decidua capsularis', 'cumulus oophorus', 'uterus')
and t.stage = 28
and gs._Assay_key = a1._Object_key
and a1._MGIType_key = 8
and a1._LogicalDB_key = 1
and a1.prefixPart = 'MGI:'
and ga._Modifiedby_key = u._User_key
;

\echo ''
\echo 'Gel Lanes where Theiler = 27 and ageMin < 21.01' or ageMin not > 28.01
\echo 'excludes (placenta,decidua,decidua basalis,decidua capsularis, cumulus oophorus'
\echo ''

select gs.age, gs.ageMin, a1.accID as mgiid, gs.laneLabel, u.login
from GXD_Assay ga, GXD_GelLane gs, GXD_GelLaneStructure r, VOC_Term s, GXD_TheilerStage t, ACC_Accession a1, VOC_Term tt, MGI_User u
where ga._AssayType_key in (1,2,3,4,5,6,8,9)
and ga._Assay_key = gs._Assay_key
and gs._GelControl_key = tt._Term_key and tt.term = 'No'
and (gs.ageMin < 21.01 or gs.ageMax > 28.01)
and gs._GelLane_key = r._GelLane_key
and r._Stage_key = t._Stage_key
and r._EMAPA_Term_key = s._Term_key
and s.term not in ('placenta','decidua','decidua basalis','decidua capsularis', 'cumulus oophorus')
and t.stage = 27
and gs._Assay_key = a1._Object_key
and a1._MGIType_key = 8
and a1._LogicalDB_key = 1
and a1.prefixPart = 'MGI:'
and ga._Modifiedby_key = u._User_key
;

\echo ''
\echo 'InSitu Specimens with Age either ''embryonic day'', ''postnatal day'', ''postnatal week'', ''postnatal month'', ''postnatal year'' but no age range entered'
\echo ''

select s.age, a.mgiID, a.jnumID, substring(s.specimenLabel, 1, 50) as specimenLabel, a.modifiedby
from GXD_Specimen s, GXD_Assay_View a
where
(
s.age ~ 'embryonic day'
or
s.age ~ 'postnatal day'
or
s.age ~ 'postnatal week'
or
s.age ~ 'postnatal month'
or
s.age ~ 'postnatal year'
)
and (s.ageMin is null or s.ageMin < 0)
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
;

\echo ''
\echo 'Gel Lane with Age either ''embryonic day'', ''postnatal day'', ''postnatal week'', ''postnatal month'', ''postnatal year'' but no age range entered'
\echo ''

select s.age, a.mgiID, a.jnumID, substring(s.laneLabel, 1, 50) as laneLabel, a.modifiedby
from GXD_GelLane s, GXD_Assay_View a, VOC_Term t
where
(
s.age ~ 'embryonic day'
or
s.age ~ 'postnatal day'
or
s.age ~ 'postnatal week'
or
s.age ~ 'postnatal month'
or
s.age ~ 'postnatal year'
)
and (s.ageMin is null or s.ageMin < 0)
and s._GelControl_key = t._Term_key and t.term = 'No'
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
;

