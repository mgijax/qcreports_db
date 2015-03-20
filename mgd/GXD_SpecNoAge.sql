set nocount on
go

select s._Assay_key, substring(s.specimenLabel, 1, 50) as specimenLabel
into #spec1
from GXD_Specimen s
where (s.age like 'Not Applicable%' or s.age like 'Not Specified%')
go

select s._Assay_key, substring(s.laneLabel, 1, 50) as laneLabel
into #spec2
from GXD_GelLane s
where s._GelControl_key = 1
and (s.age like 'Not Applicable%' or s.age like 'Not Specified%')
go

create index spec1_idx1 on #spec1(_Assay_key)
go
create index spec2_idx1 on #spec2(_Assay_key)
go

print ''
print 'InSitu Specimens with Not Applicable, Not Specified'
print ''

set nocount off
go

select a1.accID as mgiID, a2.accID as jnumID, s.specimenLabel
from #spec1 s, GXD_Assay ga, ACC_Accession a1, ACC_Accession a2
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
go

print ''
print 'Gel Lane Specimens with Not Applicable, Not Specified'
print ''

select a1.accID as mgiID, a2.accID as jnumID, s.laneLabel
from #spec2 s, GXD_Assay ga, ACC_Accession a1, ACC_Accession a2
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
go

set nocount on
go

select distinct s._Specimen_key
into #temp1
from GXD_Specimen s, GXD_InSituResult i, GXD_ISResultStructure r, GXD_Structure c, GXD_TheilerStage t
where s.age like 'postnatal%'
and s._Specimen_key = i._Specimen_key
and i._Result_key = r._Result_key
and r._Structure_key = c._Structure_key
and c._Stage_key = t._Stage_key
and t.stage != 28 
and t.stage != 27 
go

select distinct i._GelLane_key
into #temp2
from GXD_GelLane i, GXD_GelLaneStructure r, GXD_Structure s, GXD_TheilerStage t
where i.age like 'postnatal%'
and i._GelLane_key = r._GelLane_key
and r._Structure_key = s._Structure_key
and s._Stage_key = t._Stage_key
and t.stage != 28 
and t.stage != 27 
go

set nocount off
go

print ''
print 'TS 27 and TS 28 InSitu Specimens annotated to embryonic structures'
print ''

select a.mgiID, a.jnumID, substring(s.specimenLabel, 1, 50) as specimenLabel
from #temp1 t, GXD_Specimen s, GXD_Assay_View a
where t._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
go

print ''
print 'TS 27 and TS 28 Gel Lanes annotated to embryonic structures'
print ''

select a.mgiID, a.jnumID, substring(s.laneLabel, 1, 50) as laneLabel
from #temp2 t, GXD_GelLane s, GXD_Assay_View a
where t._GelLane_key = s._GelLane_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
go

print ''
print 'InSitu Specimens with Age either ''postnatal'', ''postnatal adult'', ''postnatal newborn'' but age range entered'
print ''

select s.age, a.mgiID, a.jnumID, substring(s.specimenLabel, 1, 50) as specimenLabel
from GXD_Specimen s, GXD_Assay_View a
where
(
s.age like 'postnatal [0-9]%'
or
s.age like 'postnatal adult [0-9]%'
or
s.age like 'postnatal newborn [0-9]%'
)
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
go

print ''
print 'Gel Lane Specimens with Age either ''postnatal'', ''postnatal adult'', ''postnatal newborn'' but age range entered'
print ''

select s.age, a.mgiID, a.jnumID, substring(s.laneLabel, 1, 50) as laneLabel
from GXD_GelLane s, GXD_Assay_View a
where
(
s.age like 'postnatal [0-9]%'
or
s.age like 'postnatal adult [0-9]%'
or
s.age like 'postnatal newborn [0-9]%'
)
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
go

print ''
print 'In Situ Specimens with postnatal age in (''day 0'', ''day 0.5'', ''day 1'', ''day 1.5'', ''day 2'', ''day 2.5'', ''day 3'', ''day 3.5'', ''newborn''), but not TS27'
print ''

set nocount on
go

select distinct s._Specimen_key
into #temp3
from GXD_Specimen s, GXD_InSituResult i, GXD_ISResultStructure r, GXD_Structure c, GXD_TheilerStage t
where s._Specimen_key = i._Specimen_key
and i._Result_key = r._Result_key
and r._Structure_key = c._Structure_key
and c._Stage_key = t._Stage_key
and t.stage = 27
go

create index temp3_idx on #temp3(_Specimen_key )
go

set nocount off
go

select s.age, a.mgiID, a.jnumID, substring(s.specimenLabel, 1, 50) as specimenLabel
from GXD_Specimen s, GXD_Assay_View a
where
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
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
and not exists (select 1 from #temp3 t
where s._Specimen_key = t._Specimen_key)
go

print ''
print 'Gel Lane Specimens with postnatal age in (''day 0'', ''day 0.5'', ''day 1'', ''day 1.5'', ''day 2'', ''day 2.5'', ''day 3'', ''day 3.5'', ''newborn''), but not TS27'
print ''

set nocount on
go

select distinct i._GelLane_key
into #temp4
from GXD_GelLane i, GXD_GelLaneStructure r, GXD_Structure s, GXD_TheilerStage t
where i._GelControl_key = 1
and i._GelLane_key = r._GelLane_key
and r._Structure_key = s._Structure_key
and s._Stage_key = t._Stage_key
and t.stage = 27
go

create index temp4_idx on #temp4(_GelLane_key )
go

set nocount off
go

select s.age, a.mgiID, a.jnumID, substring(s.laneLabel, 1, 50) as laneLabel
from GXD_GelLane s, GXD_Assay_View a
where
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
and s._GelControl_key = 1
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
and not exists (select 1 from #temp4 t
where s._GelLane_key = t._GelLane_key)
go
