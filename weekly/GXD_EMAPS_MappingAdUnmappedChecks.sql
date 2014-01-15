
print ''
print 'Check 9'
print 'AD Terms that do not map to EMAPS Ids'
print ''

select
	substring(acc.accId, 1, 15) as "AD ID",
	gts.stage as "TS",
	(case when vacc.annotCount = NULL then 0 else vacc.annotCount end) as "Annot Ct",
	substring(gs.printname, 1,80) as "Print Name"
from
	ACC_Accession acc,
	GXD_TheilerStage gts,
	GXD_StructureName gsn,
	GXD_Structure gs
LEFT OUTER JOIN
	VOC_Annot_Count_Cache vacc on (gs._Structure_key = vacc._Term_key and vacc.annotType = 'AD' and vacc._MGIType_key = 38)
where
	acc._MGIType_key = 38 and
	acc.prefixPart = "MGI:" and
	gs._Structure_key = acc._Object_key and
	gs._Structure_key in (
		select
			gs._Structure_key
		from
			GXD_Structure gs,
			ACC_Accession acc
		LEFT OUTER JOIN
			MGI_EMAPS_Mapping mem on (acc.accId = mem.accId)
		where
			gs._Structure_key = acc._Object_key and
			gs._Stage_key = gts._Stage_key and
			gs._StructureName_key = gsn._StructureName_key and
			acc._MGIType_key = 38 and
			acc.prefixPart = "MGI:" and
			mem.accId is NULL
	) and
	acc.accId = "MGI:4850902"
order by 
	vacc.annotCount desc
go
