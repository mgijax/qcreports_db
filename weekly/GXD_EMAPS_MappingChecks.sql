
print ''
print 'Duplicate MGI and EMAPS entries in the Mapping'
print ''

select accId, emapsId from MGI_EMAPS_Mapping group by accid + emapsid having count(*) > 1
go

print ''
print 'MGI Id''s that have no entry in the Accession Table'
print ''

select mem.accId from MGI_EMAPS_Mapping mem LEFT OUTER JOIN ACC_Accession acc on (mem.accId = acc.accID) where acc.accId is NULL
go

print ''
print 'MGI Id''s that do not map to GXD Structure terms'
print ''

select mem.accId, ty1.tableName from MGI_EMAPS_Mapping mem, ACC_MGIType ty1, ACC_Accession acc LEFT OUTER JOIN GXD_Structure gs on (acc._Object_key = gs._Structure_key) where mem.accId = acc.accId and gs._Structure_key is NULL and acc._MGIType_key = ty1._MGIType_key
go

print ''
print 'EMAPS Id''s that have no entry in the Accession Table'
print ''

select mem.emapsId from MGI_EMAPS_Mapping mem LEFT OUTER JOIN ACC_Accession acc on (mem.emapsId = acc.accID) where acc.accId is NULL
go

print ''
print 'EMAPS Id''s that do not map to Vocabulary Terms'
print ''

select mem.emapsId, ty1.tableName from MGI_EMAPS_Mapping mem, ACC_MGIType ty1, ACC_Accession acc LEFT OUTER JOIN VOC_Term voc on (acc._Object_key = voc._Term_key) where mem.emapsId = acc.accId and voc._Term_key is NULL and acc._MGIType_key = ty1._MGIType_key
go

print ''
print 'EMAPS terms that are mapped to two AD terms'
print ''

select mem.emapsId as "EMAPS ID", vte.stage as "EMAPS TS", voct.term as "EMAPS Term Name", mem.accId as "AD ID", gts.stage "AD TS", gs.printName as "AD Printname" from GXD_Structure gs, GXD_TheilerStage gts, GXD_StructureName gsn, ACC_Accession aa1, ACC_MGIType ty1, MGI_EMAPS_Mapping mem, ACC_Accession aa2, ACC_MGIType ty2, VOC_Term voct, VOC_Term_EMAPS vte where gs._Structure_key = aa1._Object_key and gs._StructureName_key = gsn._StructureName_key and gs._Stage_key = gts._Stage_key and aa1.accId = mem.accID and aa1._MGIType_key = ty1._MGIType_key and ty1.tableName = 'GXD_Structure' and mem.emapsID = aa2.accId and aa2._MGIType_key = ty2._MGIType_key and ty2.tableName = 'VOC_Term' and aa2._Object_key = voct._Term_key and voct._Term_key = vte._Term_key and mem.emapsId in ( select mem.emapsId from MGI_EMAPS_Mapping mem, ACC_Accession acc, VOC_Term voct where acc.accID = mem.emapsId and acc._Object_key = voct._Term_key and _MGIType_key = 13 group by mem.emapsId having count(mem.emapsId) > 1)
go

print ''
print 'AD terms that are mapped to two EMAPS terms'
print ''

select mem.accId as "AD ID", gts.stage "AD TS", gs.printName as "AD Printname", mem.emapsId as "EMAPS ID", vte.stage as "EMAPS TS", voct.term as "EMAPS Term Name" from GXD_Structure gs, GXD_TheilerStage gts, GXD_StructureName gsn, ACC_Accession aa1, ACC_MGIType ty1, MGI_EMAPS_Mapping mem, ACC_Accession aa2, ACC_MGIType ty2, VOC_Term voct, VOC_Term_EMAPS vte where gs._Structure_key = aa1._Object_key and gs._StructureName_key = gsn._StructureName_key and gs._Stage_key = gts._Stage_key and aa1.accId = mem.accID and aa1._MGIType_key = ty1._MGIType_key and ty1.tableName = 'GXD_Structure' and mem.emapsID = aa2.accId and aa2._MGIType_key = ty2._MGIType_key and ty2.tableName = 'VOC_Term' and aa2._Object_key = voct._Term_key and voct._Term_key = vte._Term_key and mem.accId in ( select mem.accId from GXD_Structure gs, ACC_Accession acc, MGI_EMAPS_Mapping mem where gs._Structure_key = acc._Object_key and acc._MGIType_key = 38 and mem.accId = acc.accId group by mem.accId having count(mem.accId) > 1)
go

print ''
print 'AD Stage and EMAPS Stage that are not the same'
print ''

select mem.accId as "AD ID", gts.stage "AD TS", gs.printName as "AD Printname", mem.emapsId as "EMAPS ID", vte.stage as "EMAPS TS", voct.term as "EMAPS Term Name" from GXD_Structure gs, GXD_TheilerStage gts, GXD_StructureName gsn, ACC_Accession aa1, ACC_MGIType ty1, MGI_EMAPS_Mapping mem, ACC_Accession aa2, ACC_MGIType ty2, VOC_Term voct, VOC_Term_EMAPS vte where gs._Structure_key = aa1._Object_key and gs._StructureName_key = gsn._StructureName_key and gs._Stage_key = gts._Stage_key and aa1.accId = mem.accID and aa1._MGIType_key = ty1._MGIType_key and ty1.tableName = 'GXD_Structure' and mem.emapsID = aa2.accId and aa2._MGIType_key = ty2._MGIType_key and ty2.tableName = 'VOC_Term' and aa2._Object_key = voct._Term_key and voct._Term_key = vte._Term_key and (case when convert(INT, vte.stage) = gts.stage then 1 else 0 end) = 0
go

print ''
print 'AD Terms that do not map to EMAPS Id''s'
print ''
select acc.accId as "AD ID", gts.stage as "AD TS", vacc.annotCount as "Annotation Count", gs.printname from GXD_Structure gs, GXD_TheilerStage gts, VOC_Annot_Count_Cache vacc, GXD_StructureName gsn, ACC_Accession acc LEFT OUTER JOIN MGI_EMAPS_Mapping mem on (acc.accId = mem.accId) where gs._Structure_key = acc._Object_key and gs._Stage_key = gts._Stage_key and gs._StructureName_key = gsn._StructureName_key and acc._MGIType_key = 38 and acc.prefixPart = "MGI:" and mem.accId is NULL and gs.printname not like '%obsolete%' and gs._Structure_key = vacc._Term_key and vacc.annotType = 'AD'
go

