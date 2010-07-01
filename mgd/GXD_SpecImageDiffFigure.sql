set nocount on
go

/* imageresults with images */

select distinct a._Assay_key, aa.accID, r.jnumID, r.numericPart, 
       specimen = substring(s.specimenLabel,1,50), 
       s._Specimen_key, i._Result_key,
       figureLabel = substring(ii.figureLabel, 1, 50)
into #hasimage
from GXD_Assay a, ACC_Accession aa, BIB_Citation_Cache r, 
     GXD_Specimen s, GXD_InSituResult i, GXD_InSituResultImage p, 
     IMG_ImagePane ip, IMG_Image ii
where a._Refs_key = r._Refs_key 
and a._AssayType_key in (1,6,9,10,11) 
and a._Assay_key = aa._Object_key
and aa._MGIType_key = 8
and aa._LogicalDB_key = 1
and a._Assay_key = s._Assay_key 
and s._Specimen_key = i._Specimen_key 
and i._Result_key = p._Result_key
and p._ImagePane_key = ip._ImagePane_key
and ip._Image_key = ii._Image_key
and r.jnumID not in ("J:101025", "J:103446", "J:107820", "J:122989", "J:125993",
                     "J:128545", "J:132267", "J:139122", "J:141291", "J:56618",
                     "J:80501", "J:80502", "J:91257", "J:93300", "J:157819", "J:137887")
go

/* save count of imageresults by assay/specimen/resultkey */

select h.*, imageresults = count(*)
into #imageresults
from #hasimage h
group by h._Assay_key, h._Specimen_key, h._Result_key
go

create index idx1 on #imageresults(_Assay_key)
create index idx2 on #imageresults(_Specimen_key)
create index idx3 on #imageresults(imageresults)
create index idx4 on #imageresults(figureLabel)
go

/* comparing the number of images in a assay/specimen/imageresults set */
/* if the number of images is different, then print out the row */

select distinct r.numericPart, r.jnumID, r.accID, r.specimen, r.figureLabel
into #final
from #imageresults r 
where exists (select 1 from #imageresults r2
where r._Assay_key = r2._Assay_key
and r._Specimen_key = r2._Specimen_key
and r.imageresults != r2.imageresults)
go

/* if the number of images are equal, then compare the figureLabels */

insert into #final
select distinct r.numericPart, r.jnumID, r.accID, r.specimen, r.figureLabel
from #imageresults r 
where exists (select 1 from #imageresults r2
where r._Assay_key = r2._Assay_key
and r._Specimen_key = r2._Specimen_key
and r.imageresults = r2.imageresults)
and exists (select 1 from #imageresults r2
where r._Assay_key = r2._Assay_key
and r._Specimen_key = r2._Specimen_key
and r.figureLabel != r2.figureLabel)
go

/* if counts are equall, then check that figures are equal */

set nocount off
go

print ""
print "Specimen Results with Image Annotations and Different Figures"
print ""
print "excluding references"
print "     J:101025 GenePaint"
print "     J:103446 McKee"
print "     J:107820 Cepko"
print "     J:122989 GenePaint"
print "     J:125993 GenePaint"
print "     J:128545 GenePaint"
print "     J:132267"
print "     J:139122 Manabe"
print "     J:141291 Tamplin1"
print "     J:56618"
print "     J:80501  Gitton"
print "     J:80502  Reymond"
print "     J:91257  Gray"
print "     J:93300  Blackshaw"
print "     J:157819 Blackshaw2"
print "     J:137887 JaxCre"
print ""

select * from #final
order by numericPart, accID
go

