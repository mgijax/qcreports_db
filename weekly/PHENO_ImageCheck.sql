
\echo ''
\echo 'Image Figure Labels Beginning ''Fig''.'
\echo ''

select distinct i.jnumID, i.figureLabel
from IMG_Image_View i
where i._ImageClass_key in (6481782, 6481783)
and i.figureLabel like 'Fig%'
order by i.jnumID
;

\echo ''
\echo 'Images with Copyright containing ''(||)'''
\echo ''

select distinct i.jnumID, i.figureLabel
from IMG_Image_View i, MGI_Note n, MGI_NoteChunk nc
where i._ImageClass_key in (6481782, 6481783)
and i._Image_key = n._Object_key
and n._MGIType_key = 12
and n._NoteType_key = 1023
and n._Note_key = nc._Note_key
and nc.note like '%(||)%'
order by i.jnumID
;

\echo ''
\echo 'Elsevier: where the J in the copyright does not match the J of the stub'
\echo ''

select distinct i.jnumID, i.mgiID
from IMG_Image_View i,MGI_Note_Image_View n
where i._ImageClass_key in (6481782, 6481783)
and n._NoteType_key = 1023
and lower(n.note) like 'reprinted with permission from elsevier%'
and n.note not like '%' || i.jnumID || '%'
and n._Object_key = i._Image_key
order by i.jnumID
;

\echo ''
\echo 'non-Elsevier: the first author in the copyright does not match the first author in the paper'
\echo 'includes references with pubmed ids (i.e. excludes data submission references)'
\echo ''

select distinct i.jnumID, i.mgiID, r._primary
from IMG_Image_View i,MGI_Note_Image_View n, BIB_Refs r
where i._ImageClass_key in (6481782, 6481783)
and n._NoteType_key = 1023
and lower(n.note) like 'this image is from%'
and i._Refs_key = r._Refs_key
and n.note not like '%' || substring(r._primary, 1, position(' ' in r._primary) - 1) || '%'
and n._Object_key = i._Image_key
and exists (select 1 from ACC_Accession a where r._Refs_key = a._Object_key
and a._MGIType_key = 1
and a._LogicalDB_key = 29)
order by i.jnumID
;

\echo ''
\echo 'Images with JPGs whose Thumbnails have no JPGs'
\echo ''

select distinct c.accID as "MGI ID"
from IMG_Image a, IMG_Image b, ACC_Accession c
where a._ImageClass_key in (6481782, 6481783)
and a._ImageType_key = 1072158
and a.xDim is not null
and a._ThumbnailImage_key = b._Image_key
and b.xDim is null
and a._Image_key = c._Object_key
and c._MGIType_key = 9
and c._LogicalDB_key = 1
and c.prefixPart = 'MGI:'
order by accID
;

\echo ''
\echo 'JPGs but no Copyright Statement'
\echo ''

select i.mgiID, i.jnumID
from IMG_Image_View i
where i._ImageClass_key in (6481782, 6481783)
and i._ImageType_key = 1072158
and i.xDim is not null
and not exists
(select 1 from MGI_Note mn
where i._Image_key = mn._Object_key
and mn._MGIType_key = 9
and mn._NoteType_key = 1023)
;

\echo ''
\echo 'All phenotype images (either full size or thumbnail) that lack a caption'
\echo ''

select distinct c.accID as "MGI ID"
from IMG_Image a, ACC_Accession c
where a._ImageClass_key in (6481782)
and a._Image_key = c._Object_key
and c._MGIType_key = 9
and c._LogicalDB_key = 1
and c.prefixPart = 'MGI:'
and not exists (select 1 from MGI_Note n
where a._Image_key = n._Object_key
and n._NoteType_key = 1024)
order by accID
;

\echo ''
\echo 'Multiple copyright statements for the same J#'
\echo ''

select distinct i._refs_key, regexp_replace(rtrim(nc.note), E'[\\n\\r]+', '', 'g') as notes
into temporary table notes_tmp
from IMG_Image i, MGI_Note n, MGI_NoteChunk nc
where i._ImageClass_key in (6481782, 6481783)
and i._ImageType_key = 1072158
and i._Image_key = n._Object_key
and n._NoteType_key = 1023
and n._Note_key = nc._Note_key
and i._Refs_key not in (111326, 176309)
group by i._Refs_key, regexp_replace(rtrim(nc.note), E'[\\n\\r]+', '', 'g') having count(*) > 1
;

create index notes_idx1 on notes_tmp(_refs_key)
;

with refs as (
select _Refs_key from notes_tmp
group by _Refs_key having count(*) > 1
)
select distinct c.jnumid, n.notes
from refs r, BIB_Citation_cache c, notes_tmp n
where r._Refs_key = c._Refs_key
and r._Refs_key = n._Refs_key
order by c.jnumid
;

