
/* select all Gel Assays with Image Panes */
/* exclude J:80502 */
/* exclude J:153498/Eurexpress */

select distinct a._Assay_key, a._AssayType_key, i._Refs_key, a._ImagePane_key, ip._Image_key
INTO TEMPORARY TABLE assays 
from GXD_Assay a, IMG_Image i, IMG_ImagePane ip 
where a._AssayType_key in (1,2,3,4,5,6,8,9)
and a._ImagePane_key = ip._ImagePane_key 
and ip._Image_key = i._Image_key 
and a._Refs_key not in (81463,154591)
;

/* exclude J:80502 */
/* exclude J:153498/Eurexpress */

INSERT INTO assays 
select distinct s._Assay_key, a._AssayType_key, i._Refs_key, iri._ImagePane_key, ip._Image_key
from GXD_InSituResultImage iri, GXD_InSituResult r, GXD_Specimen s, GXD_Assay a, IMG_Image i, IMG_ImagePane ip 
where iri._ImagePane_key = ip._ImagePane_key 
and ip._Image_key = i._Image_key 
and iri._Result_key = r._Result_key 
and r._Specimen_key = s._Specimen_key
and s._Assay_key = a._Assay_key
and a._Refs_key not in (81463,154591)
and a._AssayType_key in (1,2,3,4,5,6,8,9)
;

create index assays_idx1 on assays(_ImagePane_key)
;

/* assays that contain > 2 image panes */
select _ImagePane_key INTO TEMPORARY TABLE imagepane1 from assays where _AssayType_key = 6 group by _ImagePane_key having count(*) > 2
;

select _ImagePane_key INTO TEMPORARY TABLE imagepane2 from assays where _AssayType_key != 6 group by _ImagePane_key having count(*) > 1
;

create index imagepane1_idx1 on imagepane1(_ImagePane_key)
;
create index imagepane2_idx1 on imagepane2(_ImagePane_key)
;

/* select those that are annotated to more than 2 assays */

select a.* INTO TEMPORARY TABLE final 
from assays a, imagepane1 i 
where a._AssayType_key = 6
and a._ImagePane_key = i._ImagePane_key
union
select a.* 
from assays a, imagepane2 i 
where a._AssayType_key != 6
and a._ImagePane_key = i._ImagePane_key
;

create index final_idx1 on final(_Refs_key)
;
create index final_idx2 on final(_Image_key)
;

\echo ''
select count(distinct _Image_key) as "rows affected" from final
;

\echo ''
\echo 'Any Image Panes annotated to >2 assays (if Immunohistochemistry), >1 assay for all others.'
\echo 'Excludes J:80502'
\echo ''

select distinct i.accID as imageID, r.accID as refID
from final f, ACC_Accession i, ACC_Accession r  
where f._Image_key = i._Object_key 
and i._MGIType_key = 9 
and i._LogicalDB_key = 1 
and i.prefixPart = 'MGI:' 
and i.preferred = 1
and f._Refs_key = r._Object_key 
and r._MGIType_key = 1 
and r._LogicalDB_key = 1 
and r.prefixPart = 'J:' 
and r.preferred = 1
order by imageID desc
;

