set nocount on
go

select s._Assay_key, substring(s.specimenLabel, 1, 50) as specimenLabel
into #spec1
from GXD_Specimen s
where (s.age like 'Not Applicable%' or s.age like 'Not Specified%')
go

create index idx1 on #spec1(_Assay_key)
go

set nocount off
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
go

set nocount off
go

print ''
print 'InSitu Specimens with Adult Specimens annotated to embryonic structures'
print ''

select a.mgiID, a.jnumID, substring(s.specimenLabel, 1, 50) as specimenLabel
from #temp1 t, GXD_Specimen s, GXD_Assay_View a
where t._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (10,11)
go

drop table #spec1
go
drop table #temp1
go

