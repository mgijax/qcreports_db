select s._Assay_key, substring(s.specimenLabel, 1, 50) as specimenLabel
into #spec1
from GXD_Specimen s
where (s.age like 'Not Applicable%' or s.age like 'Not Specified%')
go

create index spec1_idx on #spec1(_Assay_key)
go

print ''
print 'InSitu Specimens with Not Applicable, Not Specified'
print ''

select a1.accID as mgiID, a2.accID as jnumID, s.specimenLabel
from #spec1 s, GXD_Assay ga, ACC_Accession a1, ACC_Accession a2
where s._Assay_key = ga._Assay_key
and ga._AssayType_key in (10,11)
and ga._Marker_key = a1._Object_key
and a1._MGIType_key = 2
and a1._LogicalDB_key = 1
and a1.prefixPart = 'MGI:'
and a1.preferred = 1
and ga._Refs_key = a2._Object_key
and a2._MGIType_key = 2
and a2._LogicalDB_key = 1
and a2.prefixPart = 'J:'
and a2.preferred = 1
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

print ''
print 'TS 27 and TS 28 InSitu Specimens annotated to embryonic structures'
print ''

select a.mgiID, a.jnumID, substring(s.specimenLabel, 1, 50) as specimenLabel
from #temp1 t, GXD_Specimen s, GXD_Assay_View a
where t._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (10,11)
go

print ''
print 'In Situ Specimens with postnatal age in (''day 0'', ''day 0.5'', ''day 1'', ''day 1.5'', ''day 2'', ''day 2.5'', ''day 3'', ''day 3.5'', ''newborn''), but not TS27'
print ''

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
and a._AssayType_key in (10, 11)
and not exists (select 1 from #temp3 t
where s._Specimen_key = t._Specimen_key)
go
