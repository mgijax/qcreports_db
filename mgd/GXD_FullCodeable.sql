
-- exclude any paper that contains an index stage E or A for the following assay:
-- 	in situ protein (section)
--	in situ RNA (section)
--	in situ protein (whole mount)
--	in situ RNA (whole mount)
--	in situ reporter (knock in)
--
-- exclude any paper that contains an index stage E for the following assay:
-- 	northern blot
--	western blot
--	RT-PCR
--	RNase protection
--	nuclease S1
-- 
-- exclude any paper that has the following assay:
-- 	cDNA clones 
--	primer extension

set nocount on
go

select distinct gi._Refs_key 
into #refs_excluded
from GXD_Index gi, GXD_Index_Stages gs
where gi._Index_key = gs._Index_key
and ((gs._IndexAssay_key in (74717, 74718, 74719, 74720, 74721) and gs._StageID_key in (74769, 74770))
or  (gs._IndexAssay_key in (74722, 74723, 74724, 74726, 74727) and gs._StageID_key = 74769)
or  (gs._IndexAssay_key in (74725, 74728)))
go

create index idx1 on #refs_excluded(_Refs_key)
go

select g._Marker_key, ref_count = count(*)
into #refs_summary
from GXD_Index g
where not exists (select 1 from #refs_excluded r where r._Refs_key = g._Refs_key)
and not exists (select 1 from GXD_Assay a where a._Marker_key = g._Marker_key)
group by g._Marker_key
go

create index idx1 on #refs_summary(_Marker_key)
go

set nocount off
go

print ""
print "Genes that have not been full coded that have full codeable papers"
print ""

select m.symbol, r.ref_count "codeable papers"
from #refs_summary r, MRK_Marker m
where r._Marker_key = m._Marker_key
order by ref_count desc, m.symbol
go

