\echo ''
\echo 'GXD Image Figure Labels Beginning ''Fig''.'
\echo ''

select distinct i.jnumID, i.figureLabel
from IMG_Image_View i
where i._ImageClass_key = 6481781
and i.figureLabel like 'Fig%'
order by i.jnumID
;

\echo ''
\echo 'GXD Images with Copyright containing ''(||)'''
\echo ''

select distinct i.jnumID, i.figureLabel
from IMG_Image_View i, MGI_Note n, MGI_NoteChunk nc
where i._ImageClass_key = 6481781
and i._Image_key = n._Object_key
and n._MGIType_key = 9
and n._NoteType_key = 1023
and n._Note_key = nc._Note_key
and nc.note like '%(||)%'
order by i.jnumID
;

\echo ''
\echo 'Elsevier: where the J in the copyright does not match the J of the stub'
\echo ''

select distinct i.jnumID, i.mgiID
from IMG_Image_View i, MGI_Note_Image_View n
where i._ImageClass_key = 6481781
and n._NoteType_key = 1023
and lower(n.note) like 'reprinted with permission from elsevier%'
and n.note not like '%' || i.jnumID || '%'
and n._Object_key = i._Image_key
order by i.jnumID
;

\echo ''
\echo 'non-Elsevier: the first author in the copyright does not match the first author in the paper'
\echo 'exclude: J:228563'
\echo ''

select distinct i.jnumID, i.mgiID, r._primary, 
       n.note, substring(r._primary, 1, position(' ' in r._primary) - 1) as p
into temporary table author_tmp
from IMG_Image_View i, MGI_Note_Image_View n, BIB_Refs r
where i._ImageClass_key = 6481781
and n._NoteType_key = 1023
and lower(n.note) like 'this image is from%'
and i._Refs_key not in (229658)
and i._Refs_key = r._Refs_key
and n._Object_key = i._Image_key
;

select jnumID, mgiID, _primary
from author_tmp
where note not like '%' || p || '%'
order by jnumID
;

\echo ''
\echo 'JPGs but no Copyright Statement'
\echo ''

select i.mgiID, i.jnumID
from IMG_Image_View i 
where i._ImageClass_key = 6481781
and i._ImageType_key = 1072158
and i.xDim is not null
and not exists
(select 1 from MGI_Note mn
where i._Image_key = mn._Object_key
and mn._MGIType_key = 9
and mn._NoteType_key = 1023)
;

\echo ''
\echo 'Multiple copyright statements for the same J#'
\echo ''

select distinct i._refs_key, trim(regexp_replace(rtrim(nc.note), E'[\\n\\r]+', '', 'g')) as notes
into temporary table notes_tmp
from IMG_Image i, MGI_Note n, MGI_NoteChunk nc
where i._ImageClass_key = 6481781
and i._ImageType_key = 1072158
and i._Image_key = n._Object_key
and n._NoteType_key = 1023
and n._Note_key = nc._Note_key
and i._Refs_key not in (102083,104515,127085,129637,140270,144871,154591,158912,163316,172505,185674,185675,217962,227123,94290)
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

