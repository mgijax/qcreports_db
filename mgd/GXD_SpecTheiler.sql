set nocount on
go

select distinct i._Specimen_key, t.stage
into #temp1
from GXD_InSituResult i, GXD_ISResultStructure r, GXD_Structure s, GXD_TheilerStage t
where i._Result_key = r._Result_key
and r._Structure_key = s._Structure_key
and s._Stage_key = t._Stage_key
and t.stage != 28
union
select distinct i._Specimen_key, t.stage
from GXD_InSituResult i, GXD_ISResultStructure r, GXD_Structure s, GXD_TheilerStage t,
GXD_StructureName sn
where i._Result_key = r._Result_key
and r._Structure_key = s._Structure_key
and s._Stage_key = t._Stage_key
and t.stage = 28
and s._StructureName_key = sn._StructureName_key
and (sn.structure = "placenta" or sn.structure = "decidua")
go

select distinct _Specimen_key 
into #temp2
from #temp1
group by _Specimen_key
having count(*) > 1
go

select distinct i._GelLane_key, t.stage
into #temp3
from GXD_GelLane i, GXD_GelLaneStructure r, GXD_Structure s, GXD_TheilerStage t
where i.age not like "%-%"
and i.age not like "%,%"
and i._GelLane_key = r._GelLane_key
and r._Structure_key = s._Structure_key
and s._Stage_key = t._Stage_key
and t.stage != 28
go

select distinct _GelLane_key 
into #temp4
from #temp3
group by _GelLane_key
having count(*) > 1
go

set nocount off
go

print ""
print "InSitu Specimens annotated to structures of > 1 Theiler Stage"
print "(excludes stage 28)"
print ""

select a.mgiID, a.jnumID, specimenLabel = substring(s.specimenLabel, 1, 50)
from #temp2 t, GXD_Specimen s, GXD_Assay_View a
where t._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
go

print ""
print "Gel Lane Specimens annotated to structures of > 1 Theiler Stage"
print "(excludes stage 28)"
print ""

select a.mgiID, a.jnumID, laneLabel = substring(s.laneLabel, 1, 50)
from #temp4 t, GXD_GelLane s, GXD_Assay_View a
where t._GelLane_key = s._GelLane_key
and s._Assay_key = a._Assay_key
go
