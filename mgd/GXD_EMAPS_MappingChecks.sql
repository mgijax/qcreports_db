
/* Changes: */
/* TR11915 - Update to Check 4 - 01/23/2015 - sc */

\echo ''
\echo 'Check 1'
\echo 'Duplicate MGI and EMAPS entries in the Mapping Table'
\echo ''

select
	accId,
	emapsId
from
	MGI_EMAPS_Mapping
group by
	accid , emapsid
having
	count(*) > 1
;

\echo ''
\echo 'Check 2'
\echo 'MGI Id''s that do not have an entry in the Accession Table'
\echo ''

select
	mem.accId
from
	MGI_EMAPS_Mapping mem
LEFT OUTER JOIN
	ACC_Accession acc on (mem.accId = acc.accID)
where
	acc.accId is NULL
;

\echo ''
\echo 'Check 3'
\echo 'MGI Id''s that do not map to GXD Structures in the GXD_Structure table'
\echo 'May have multiple entries if MGI Id maps to other objects'
\echo ''

select
	distinct
	mem.accId,
	substring(ty1.tableName, 1, 20) as "Object Name"
from
	MGI_EMAPS_Mapping mem,
	ACC_MGIType ty1,
	ACC_Accession acc
LEFT OUTER JOIN
	GXD_Structure gs on (acc._Object_key = gs._Structure_key and acc._MGIType_key = 38)
where
	mem.accId = acc.accId and
	gs._Structure_key is NULL and
	acc._MGIType_key = ty1._MGIType_key

;

\echo ''
\echo 'Check 4'
\echo 'Id''s in the EMAPS Field that do not have an entry in the Accession Table'
\echo ''

select mem.emapsId, mem.accID as adID
INTO TEMPORARY TABLE invalidIDs
from MGI_EMAPS_Mapping mem
	LEFT OUTER JOIN
	ACC_Accession acc on (mem.emapsId = acc.accID)
where acc.accId is NULL
;

create index invalidIDs_idx on invalidIDs(adID)
;

select _Structure_key, count(_Structure_key) as aCt
INTO TEMPORARY TABLE annotCt
from GXD_Expression
group by _structure_key
;

create index annotCt_idx on annotCt(_Structure_key)
;

select i.adID, i.emapsId, ac.aCt
from invalidIDs i, ACC_Accession a, annotCt ac
where i.adID = a.accID
and a._MGIType_key = 38
and a._LOgicalDB_key = 1
and a._Object_key = ac._Structure_key
;

\echo ''
\echo 'Check 5'
\echo 'IDs in the EMAPS field that are not valid EMAPS IDs'
\echo ''

select
	distinct
	mem.emapsId,
	substring(ty1.tableName, 1, 25) as "Object type"
from
	MGI_EMAPS_Mapping mem,
	ACC_MGIType ty1,
	ACC_Accession acc
LEFT OUTER JOIN
	VOC_Term_EMAPS vte on (acc._Object_key = vte._Term_key)
where
	mem.emapsId = acc.accId and
	vte._Term_key is NULL and
	acc._MGIType_key = ty1._MGIType_key
;

\echo ''
\echo 'Check 6'
\echo 'EMAPS terms that are mapped to two AD terms'
\echo ''

select
	substring(mem.emapsId, 1, 15) as "EMAPS ID",
	substring(vte.stage, 1, 5) as "EMAPS TS",
	substring(voct.term, 1, 35) as "EMAPS Term Name",
	substring(mem.accId, 1, 15) as "AD ID",
	gts.stage as "AD TS",
	substring(gs.printName, 1,35) as "AD Printname"
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
	mem.emapsId in (
		select
			mem.emapsId
		from
			MGI_EMAPS_Mapping mem,
			ACC_Accession acc,
			VOC_Term voct
		where
			acc.accID = mem.emapsId and
			acc._Object_key = voct._Term_key and
			_MGIType_key = 13
		group by
			mem.emapsId
		having
			count(mem.emapsId) > 1
	)
;

\echo ''
\echo 'Check 7'
\echo 'AD terms that are mapped to two EMAPS terms'
\echo ''

select
	substring(mem.accId, 1, 15) as "AD ID",
	gts.stage as  "AD TS",
	substring(gs.printName, 1,35) as "AD Printname",
	substring(mem.emapsId, 1, 15) as "EMAPS ID",
	substring(vte.stage, 1, 5) as "EMAPS TS",
	substring(voct.term, 1,35) as "EMAPS Term Name"
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
	mem.accId in (
		select
			mem.accId
		from
			GXD_Structure gs,
			ACC_Accession acc,
			MGI_EMAPS_Mapping mem
		where
			gs._Structure_key = acc._Object_key and
			acc._MGIType_key = 38 and
			mem.accId = acc.accId
		group by
			mem.accId
		having
			count(mem.accId) > 1
	)
;

\echo ''
\echo 'Check 8'
\echo 'AD Stage and EMAPS Stage that are not the same'
\echo ''

select
	substring(mem.accId, 1, 15) as "AD ID",
	gts.stage as "AD TS",
	substring(gs.printName, 1,35) as "AD Printname",
	substring(mem.emapsId, 1, 15) as "EMAPS ID",
	substring(vte.stage, 1, 5) as "EMAPS TS",
	substring(voct.term, 1,35) as "EMAPS Term Name"
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
	(case when vte.stage::int = gts.stage then 1 else 0 end) = 0
;

