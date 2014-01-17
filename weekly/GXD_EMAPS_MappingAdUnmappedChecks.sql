
print ''
print 'Check 9'
print 'AD Terms that do not map to EMAPS Ids'
print ''

	select
		gs._Structure_key,
		count(gs._Structure_key) as "SCount"
	into #tmp_olin
	from
		GXD_Structure gs,
		ACC_Accession acc
	LEFT OUTER JOIN
		MGI_EMAPS_Mapping mem on (acc.accId = mem.accId)
	LEFT OUTER JOIN
		GXD_Expression ge on (acc._Object_key = ge._Structure_key and isForGXD = 1)
	where
		gs._Structure_key = acc._Object_key and
		acc._MGIType_key = 38 and
		acc.prefixPart = "MGI:" and
		mem.accId is NULL and
		ge._Structure_key is not NULL
	group by
		gs._Structure_key
union
	select
		gs._Structure_key,
		0 as "SCount"
	from
		GXD_Structure gs,
		ACC_Accession acc
	LEFT OUTER JOIN
		MGI_EMAPS_Mapping mem on (acc.accId = mem.accId)
	LEFT OUTER JOIN
		GXD_Expression ge on (acc._Object_key = ge._Structure_key and isForGXD = 1)
	where
		gs._Structure_key = acc._Object_key and
		acc._MGIType_key = 38 and
		acc.prefixPart = "MGI:" and
		mem.accId is NULL and
		ge._Structure_key is NULL
	group by
		gs._Structure_key

select
	substring(acc.accId, 1, 15) as "AD ID",
	convert(varchar(5), gts.stage) as "AD TS",
	convert(varchar(5), olin.Scount) as "Annot Count",
	substring(gs.printname, 1,80) as "Term"
from
	#tmp_olin olin,
	GXD_Structure gs,
	ACC_Accession acc,
	GXD_TheilerStage gts
where
	olin._Structure_key = gs._Structure_key and
	gs._Structure_key = acc._Object_key and
	gs._Stage_key = gts._Stage_key and
	acc._MGIType_key = 38 and
	acc.prefixPart = "MGI:"
order by
	olin.SCount desc, "Term"

drop table #tmp_olin

go
