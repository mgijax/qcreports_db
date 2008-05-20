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
and not (t.stage = 28 and (sn.structure = "placenta" or sn.structure = "decidua"))
go

select distinct _Specimen_key 
into #temp2
from #temp1
group by _Specimen_key
having count(*) > 1
go

set nocount off
go

print ""
print "InSitu Specimens annotated to structures of > 1 Theiler Stage"
print "(excludes TS28:placenta, TS28:decidua)"
print ""

select a.mgiID, a.jnumID, specimenLabel = substring(s.specimenLabel, 1, 50)
from #temp2 t, GXD_Specimen s, GXD_Assay_View a
where t._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (10,11)
go

set nocount on
go

/* Added 8/16/2007 TR8389 */

/* get the structure key for reproductive system */
select distinct _Structure_key
into #repro
from GXD_StructureName
where structure = "reproductive system"
go

/* get all children of "reproductive system" */
select distinct _Descendent_key
into #child
from GXD_StructureClosure
where _Structure_key in (
select _Structure_key
from #repro)
go

/* get the structure key for "female" */
select distinct _Structure_key
into #reproF
from #child c, GXD_StructureName sn
where c._Descendent_key = sn._Structure_key
and sn.structure = "female"
go

/* get all children of "female" */
select distinct _Descendent_key
into #fChild
from GXD_StructureClosure
where _Structure_key in (
select _Structure_key
from  #reproF)

/* union female and its childrend */ 
select _Structure_key
into #allFStruct
from #reproF
union
select _Descendent_key as _Structure_key
from #fChild
go

/* get info about "reproductive system;female" and children */
select distinct s._Specimen_key, s.specimenLabel, a.jnumID, a.mgiID
into #fSpecimens
from GXD_Specimen s, GXD_Assay_View a, GXD_InSituResult ir, GXD_ISResultStructure irs
where s._Assay_key = a._Assay_key
and a._AssayType_key in (10,11)
and s._Specimen_key = ir._Specimen_key
and ir._Result_key = irs._Result_key
and irs._Structure_key in (
select distinct _Structure_key
from #allFStruct)
go

/* do same as above for male */
select distinct _Structure_key
into #reproM
from #child c, GXD_StructureName sn
where c._Descendent_key = sn._Structure_key
and sn.structure = "male"
go

select distinct _Descendent_key
into #mChild
from GXD_StructureClosure
where _Structure_key in (
select _Structure_key
from  #reproM)

select _Structure_key
into #allMStruct
from #reproM
union
select _Descendent_key as _Structure_key
from #mChild
go

select distinct s._Specimen_key
into #mSpecimens
from GXD_Specimen s, GXD_Assay_View a, GXD_InSituResult ir, GXD_ISResultStructure irs
where s._Assay_key = a._Assay_key
and a._AssayType_key in (10,11)
and s._Specimen_key = ir._Specimen_key
and ir._Result_key = irs._Result_key
and irs._Structure_key in (
select distinct _Structure_key
from #allMStruct)

go

set nocount off
go

print ""
print "InSitu Specimens with > 1 Sex" 
print ""

/* report all specimens with annotated to both male and female structures */
select distinct mgiID, jnumID, substring(specimenLabel,1,50) as specimenLabel
from #fSpecimens f, #mSpecimens m
where f._Specimen_key = m._Specimen_key
order by mgiID, jnumID
go
