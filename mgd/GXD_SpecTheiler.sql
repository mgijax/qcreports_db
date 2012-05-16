/* TR10731/added 'mesometrium' */

set nocount on
go

select distinct i._Specimen_key, t.stage
into #temp1
from GXD_InSituResult i, GXD_ISResultStructure r, GXD_Structure s, GXD_TheilerStage t,
GXD_StructureName sn
where i._Result_key = r._Result_key
and r._Structure_key = s._Structure_key
and s._Stage_key = t._Stage_key
and s._StructureName_key = sn._StructureName_key
and not (t.stage = 28 
and sn.structure in ('placenta','decidua','decidua basalis','decidua capsularis'))
go

select distinct _Specimen_key 
into #temp2
from #temp1
group by _Specimen_key having count(*) > 1
go

select distinct i._GelLane_key, t.stage
into #temp3
from GXD_GelLane i, GXD_GelLaneStructure r, GXD_Structure s, GXD_TheilerStage t,
GXD_StructureName sn
where i.age not like '%-%'
and i.age not like '%,%'
and i._GelLane_key = r._GelLane_key
and r._Structure_key = s._Structure_key
and s._Stage_key = t._Stage_key
and s._StructureName_key = sn._StructureName_key
and not (t.stage = 28 and sn.structure in ('placenta','decidua','decidua basalis','decidua capsularis','uterus', 'mesometrium'))
go

select distinct _GelLane_key 
into #temp4
from #temp3
group by _GelLane_key having count(*) > 1
go

set nocount off
go

print ''
print 'InSitu Specimens annotated to structures of > 1 Theiler Stage'
print '(excludes TS28:placenta, TS28:decidua, TS28:decidua basalis, TS28:decidua capsularis)'
print ''

select a.mgiID, a.jnumID, substring(s.specimenLabel, 1, 50) as specimenLabel
from #temp2 t, GXD_Specimen s, GXD_Assay_View a
where t._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
go

print ''
print 'Gel Lane Specimens annotated to structures of > 1 Theiler Stage'
print '(excludes TS28:placenta, TS28:decidua, TS28:decidua basalis, TS28:decidua capsularis, TS28:uterus, TS28:mesometrium)'
print ''

select a.mgiID, a.jnumID, substring(s.laneLabel, 1, 50) as laneLabel
from #temp4 t, GXD_GelLane s, GXD_Assay_View a
where t._GelLane_key = s._GelLane_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
go

set nocount on
go

/* Added 8/16/2007 TR8389 */

/* get all children of 'reproductive system' */
select distinct sc._Descendent_key
into #repChild
from GXD_StructureName sn, GXD_StructureClosure sc
where sn.structure = 'reproductive system'
and sn._Structure_key = sc._Structure_key
go

/* get all children of 'female' */
select distinct sn._Structure_key
into #femaleChild
from #repChild c, GXD_StructureName sn
where c._Descendent_key = sn._Structure_key
and sn.structure = 'female'
union
select distinct sc._Descendent_key
from #repChild c, GXD_StructureName sn, GXD_StructureClosure sc
where c._Descendent_key = sn._Structure_key
and sn.structure = 'female'
and sn._Structure_key = sc._Structure_key
go

/* get all children of 'male' */
select distinct sn._Structure_key
into #maleChild
from #repChild c, GXD_StructureName sn
where c._Descendent_key = sn._Structure_key
and sn.structure = 'male'
union
select distinct sc._Descendent_key
from #repChild c, GXD_StructureName sn, GXD_StructureClosure sc
where c._Descendent_key = sn._Structure_key
and sn.structure = 'male'
and sn._Structure_key = sc._Structure_key
go

/* get info about 'reproductive system;female' and children */
select distinct s._Specimen_key, s.specimenLabel, a.jnumID, a.mgiID
into #fSpecimens
from GXD_Specimen s, GXD_Assay_View a, GXD_InSituResult ir, GXD_ISResultStructure irs, #femaleChild f
where s._Assay_key = a._Assay_key
and a._AssayType_key in (10,11)
and s._Specimen_key = ir._Specimen_key
and ir._Result_key = irs._Result_key
and irs._Structure_key = f._Structure_key
go

/* get info about 'reproductive system;male' and children */
select distinct s._Specimen_key
into #mSpecimens
from GXD_Specimen s, GXD_Assay_View a, GXD_InSituResult ir, GXD_ISResultStructure irs, #maleChild m
where s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
and s._Specimen_key = ir._Specimen_key
and ir._Result_key = irs._Result_key
and irs._Structure_key = m._Structure_key
go

set nocount off
go

print ''
print 'InSitu Specimens and Gel Lanes with > 1 Sex' 
print '(excludes J:80502)'
print ''

/* report all specimens with annotated to both male and female structures */
select distinct mgiID, jnumID, substring(specimenLabel,1,50) as specimenLabel
from #fSpecimens f, #mSpecimens m
where f._Specimen_key = m._Specimen_key
and f.jnumID != 'J:80502'
order by mgiID, jnumID
go

