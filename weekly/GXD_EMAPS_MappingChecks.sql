
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
print 'Duplicate MGI Id in the Mapping table for one AD term in the Structure table'
print ''

select mem.accId from GXD_Structure gs, ACC_Accession acc, MGI_EMAPS_Mapping mem where gs._Structure_key = acc._Object_key and acc._MGIType_key = 38 and mem.accId = acc.accId group by mem.accId having count(mem.accId) > 1
go

print ''
print 'AD Terms that do not map to EMAPS Id''s'
print ''
select acc.accId, gsn.structure from GXD_Structure gs, GXD_StructureName gsn, ACC_Accession acc LEFT OUTER JOIN MGI_EMAPS_Mapping mem on (acc.accId = mem.accId) where gs._Structure_key = acc._Object_key and gs._StructureName_key = gsn._StructureName_key and acc._MGIType_key = 38 and acc.prefixPart = "MGI:" and mem.accId is NULL
go

print ''
print 'AD Term names and EMAPS Term names that do not match'
print ''
select mem.accId, gsn.structure, voct.term, mem.emapsId from GXD_Structure gs, GXD_TheilerStage gts, GXD_StructureName gsn, ACC_Accession aa1, ACC_MGIType ty1, MGI_EMAPS_Mapping mem, ACC_Accession aa2, ACC_MGIType ty2, VOC_Term voct, VOC_Term_EMAPS vte where gs._Structure_key = aa1._Object_key and gs._StructureName_key = gsn._StructureName_key and gs._Stage_key = gts._Stage_key and aa1.accId = mem.accID and aa1._MGIType_key = ty1._MGIType_key and ty1.tableName = 'GXD_Structure' and mem.emapsID = aa2.accId and aa2._MGIType_key = ty2._MGIType_key and ty2.tableName = 'VOC_Term' and aa2._Object_key = voct._Term_key and voct._Term_key = vte._Term_key and (case when voct.term = gsn.structure then 1 else 0 end) = 0
go

print ''
print 'AD Stage and EMAPS Stage that are not the same'
print ''

select mem.accId, gts.stage, mem.emapsId, vte.stage from GXD_Structure gs, GXD_TheilerStage gts, GXD_StructureName gsn, ACC_Accession aa1, ACC_MGIType ty1, MGI_EMAPS_Mapping mem, ACC_Accession aa2, ACC_MGIType ty2, VOC_Term voct, VOC_Term_EMAPS vte where gs._Structure_key = aa1._Object_key and gs._StructureName_key = gsn._StructureName_key and gs._Stage_key = gts._Stage_key and aa1.accId = mem.accID and aa1._MGIType_key = ty1._MGIType_key and ty1.tableName = 'GXD_Structure' and mem.emapsID = aa2.accId and aa2._MGIType_key = ty2._MGIType_key and ty2.tableName = 'VOC_Term' and aa2._Object_key = voct._Term_key and voct._Term_key = vte._Term_key and (case when convert(INT, vte.stage) = gts.stage then 1 else 0 end) = 0
go
