/* TR11507 exclude nuclease S1 and RNase protection */
/* TR 7370 */
/* TR 9563 */
/* TR 9646: add ''binding'' and ''rocket'' to exclusion list */
/* TR 10642 add ''%quantitative RT%'' to exclusion list */

/* exclude cDNA (74725) and primer extension (74728) */
/* 1/28/14 exclude RNAse prot (74727) and S1 nuc (74726) */

select distinct gi._Index_key
into #excluded
from GXD_Index gi, GXD_Index_Stages gs 
where gi._Index_key = gs._Index_key
and gs._IndexAssay_key in (74725, 74726, 74727, 74728)
and not exists (select 1 from GXD_Index_Stages gs2
where gi._Index_key = gs2._Index_key
and gs2._IndexAssay_key not in (74725,  74726, 74727, 74728))
go

/* exclude E? */

insert into #excluded
select distinct gi._Index_key
from GXD_Index gi, GXD_Index_Stages gs 
where gi._Index_key = gs._Index_key
and gs._StageID_key = 74769
and not exists (select 1 from GXD_Index_Stages gs2
where gi._Index_key = gs2._Index_key
and gs2._StageID_key != 74769)
go

insert into #excluded
select _Index_key from GXD_Index
where lower(comments) like '%ot blot%'
or lower(comments) like '%fraction%'
or lower(comments) like '%reverse%'
or lower(comments) like '%immunoprecip%'
or lower(comments) like '%binding%'
or lower(comments) like '%rocket%'
or lower(comments) like '%quantitative RT%'
go

create index excluded_idx on #excluded(_Index_key)
go

\echo ''
\echo 'Full Coded References that contain indexed Genes that have not been full coded'
\echo ''
\echo 'excluded:'
\echo '     index records that contain only cDNA, primer extension, nuclease S1 and RNase protection assays'
\echo '     index records that contain only age ''E?'''
\echo '     index records that have a note that contains: '
\echo '     ''ot blot'', ''fraction'', ''reverse'', ''immunoprecip'', ''binding'', ''rocket'', ''quantitative RT'''
\echo ''

select distinct b.accID, m.symbol, b.numericPart
from GXD_Index i, MRK_Marker m, ACC_Accession b
where not exists (select 1 from #excluded e where i._Index_key = e._Index_key)
and exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key and a._AssayType_key in (1,2,3,4,5,6,8,9))
and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key and a._AssayType_key in (1,2,3,4,5,6,8,9)
and i._Marker_key = a._Marker_key)
and i._Marker_key = m._Marker_key
and i._Refs_key = b._Object_key
and b._MGIType_key = 1
and b._LogicalDB_key = 1
and b.prefixPart = 'J:'
order by b.numericPart
go

