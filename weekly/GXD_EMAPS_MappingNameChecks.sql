
print ''
print 'Check 10'
print 'AD Term names and EMAPS Term names that do not match'
print ''
select
	substring(mem.accId, 1, 15) as "AD ID",
	string(gts.stage) as "AD TS",
	substring(gs.printName, 1,80) as "AD PrintName",
	substring(mem.emapsId, 1, 15) as "EMAPS ID",
	vte.stage as "EMAPS TS",
	substring(voct.term, 1,80) as "EMAPS Term Name"
from
	GXD_Structure gs,
	GXD_TheilerStage gts,
	GXD_StructureName gsn,
	ACC_Accession aa1,
	ACC_MGIType ty1,
	MGI_EMAPS_Mapping mem,
	ACC_Accession aa2,
	ACC_MGIType ty2,
	VOC_Term voct,
	VOC_Term_EMAPS vte
where
	gs._Structure_key = aa1._Object_key and
	gs._StructureName_key = gsn._StructureName_key and
	gs._Stage_key = gts._Stage_key and
	aa1.accId = mem.accID and
	aa1._MGIType_key = ty1._MGIType_key and
	ty1.tableName = 'GXD_Structure' and
	mem.emapsID = aa2.accId and
	aa2._MGIType_key = ty2._MGIType_key and
	ty2.tableName = 'VOC_Term' and
	aa2._Object_key = voct._Term_key and
	voct._Term_key = vte._Term_key and
	(case when voct.term = gsn.structure then 1 else 0 end) = 0
go

