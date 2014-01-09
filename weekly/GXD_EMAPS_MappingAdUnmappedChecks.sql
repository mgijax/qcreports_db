
print ''
print 'AD Terms that do not map to EMAPS Id''s - Showing obsolete terms in the name'
print ''
select acc.accId as "AD ID", gts.stage as "AD TS", vacc.annotCount as "Annotation Count", gs.printname as "Print Name" from GXD_Structure gs, GXD_TheilerStage gts, VOC_Annot_Count_Cache vacc, GXD_StructureName gsn, ACC_Accession acc LEFT OUTER JOIN MGI_EMAPS_Mapping mem on (acc.accId = mem.accId) where gs._Structure_key = acc._Object_key and gs._Stage_key = gts._Stage_key and gs._StructureName_key = gsn._StructureName_key and acc._MGIType_key = 38 and acc.prefixPart = "MGI:" and mem.accId is NULL and gs._Structure_key = vacc._Term_key and vacc.annotType = 'AD'
go

