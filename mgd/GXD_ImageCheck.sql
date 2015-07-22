
/* select all Gel Assays with Image Panes that have JPGs (xDim is not null) */

select distinct a._Assay_key, a._ImagePane_key, ip._Image_key
INTO TEMPORARY TABLE assays 
from GXD_Assay a, IMG_Image i, IMG_ImagePane ip 
where a._AssayType_key in (1,2,3,4,5,6,8,9)
and a._ImagePane_key = ip._ImagePane_key 
and ip._Image_key = i._Image_key 
and i.xDim is not null
;

/* select all InSitu Assays with Image Panes that have JPGs (xDim is not null) */

INSERT INTO assays 
select distinct s._Assay_key, iri._ImagePane_key, ip._Image_key
from GXD_InSituResultImage iri, GXD_InSituResult r, GXD_Specimen s, GXD_Assay a, IMG_Image i, IMG_ImagePane ip 
where iri._ImagePane_key = ip._ImagePane_key 
and ip._Image_key = i._Image_key 
and i.xDim is not null 
and iri._Result_key = r._Result_key 
and r._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
and a._AssayType_key in (1,2,3,4,5,6,8,9)
;

create index assays_idx1 on assays(_ImagePane_key)
;

\echo ''
\echo 'GXD Image Figure Labels Beginning ''Fig''.'
\echo ''

select distinct i.jnumID, i.figureLabel
from IMG_Image_View i
where i.figureLabel like 'Fig%'
order by i.jnumID
;

\echo ''
\echo 'GXD Images with Copyright containing ''(||)'''
\echo ''

select distinct i.jnumID, i.figureLabel
from IMG_Image_View i, MGI_Note n, MGI_NoteChunk nc
where i._MGIType_key = 8
and i._Image_key = n._Object_key
and n._MGIType_key = 9
and n._NoteType_key = 1023
and n._Note_key = nc._Note_key
and nc.note like '%(||)%'
order by i.jnumID
;

\echo ''
\echo 'GXD Image Pane Labels containing a comma'
\echo ''

select distinct i.jnumID, i.figureLabel
from IMG_Image_View i, IMG_ImagePane p
where p.paneLabel like '%,%' and p._Image_key = i._Image_key
order by i.jnumID
;

\echo ''
\echo 'Elsevier: where the J in the copyright does not match the J of the stub'
\echo ''

select distinct i.jnumID, i.mgiID
from IMG_Image_View i, MGI_Note_Image_View n
where i._MGIType_key = 8
and n._NoteType_key = 1023
and lower(n.note) like 'reprinted with permission from elsevier%'
and n.note not like '%' || i.jnumID || '%'
and n._Object_key = i._Image_key
order by i.jnumID
;

\echo ''
\echo 'non-Elsevier: the first author in the copyright does not match the first author in the paper'
\echo ''

select distinct i.jnumID, i.mgiID, r._primary, 
       n.note, substring(r._primary, 1, charindex(' ', r._primary) - 1) as p
INTO TEMPORARY TABLE a
from IMG_Image_View i, MGI_Note_Image_View n, BIB_Refs r
where i._MGIType_key = 8
and n._NoteType_key = 1023
and lower(n.note) like 'this image is from%'
and i._Refs_key = r._Refs_key
and n._Object_key = i._Image_key
;

select jnumID, mgiID, _primary
from a
where note not like '%' || p || '%'
order by jnumID
;

\echo ''
\echo 'JPGs but no Copyright Statement'
\echo ''

select i.mgiID, i.jnumID
from IMG_Image_View i 
where i._MGIType_key = 8
and i._ImageType_key = 1072158
and i.xDim is not null
and not exists
(select 1 from MGI_Note mn
where i._Image_key = mn._Object_key
and mn._MGIType_key = 9
and mn._NoteType_key = 1023)
;

