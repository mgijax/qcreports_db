set nocount on
go

/* results with images */

select a._Assay_key, aa.accID, r.jnumID, r.numericPart, specimen = substring(s.specimenLabel,1,50), 
       i._Specimen_key, i._Result_key, i.sequenceNum
into #hasimage
from GXD_Assay a, ACC_Accession aa, BIB_Citation_Cache r, 
     GXD_Specimen s, GXD_InSituResult i, GXD_InSituResultImage p
where a._Refs_key = r._Refs_key 
and a._AssayType_key in (1,6,9,10,11) 
and a._Assay_key = aa._Object_key
and aa._MGIType_key = 8
and aa._LogicalDB_key = 1
and a._Assay_key = s._Assay_key 
and s._Specimen_key = i._Specimen_key 
and i._Result_key = p._Result_key
and r.jnumID not in ("J:101025", "J:103446", "J:107820", "J:122989", "J:125993",
                     "J:128545", "J:132267", "J:139122", "J:141291", "J:56618",
                     "J:80501", "J:80502", "J:91257", "J:93300")
go

/* results without images */
/* where the results are from the same specimens in hasimage */

select a._Assay_key, aa.accID, r.jnumID, r.numericPart, specimen = substring(s.specimenLabel,1,50), 
       i._Specimen_key, i._Result_key, i.sequenceNum
into #noimage
from GXD_Assay a, ACC_Accession aa, BIB_Citation_Cache r, GXD_Specimen s, GXD_InSituResult i
where a._Refs_key = r._Refs_key 
and a._AssayType_key in (1,6,9,10,11) 
and a._Assay_key = s._Assay_key 
and a._Assay_key = aa._Object_key
and aa._MGIType_key = 8
and aa._LogicalDB_key = 1
and s._Specimen_key = i._Specimen_key 
and exists (select 1 from #hasimage p where s._Specimen_key = p._Specimen_key)
and not exists (select 1 from GXD_InSituResultImage p where i._Result_key = p._Result_key)
go

create index idx1 on #hasimage(_Specimen_key)
create index idx1 on #noimage(_Specimen_key)
go

select distinct #noimage._Specimen_key
into #missingimage 
from #hasimage, #noimage where #hasimage._Specimen_key = #noimage._Specimen_key
go

create index idx1 on #missingimage(_Specimen_key)
go

set nocount off
go

print ""
print "Specimen Results with Incomplete Image Annotations"
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
print "     J:80501 Gitton"
print "     J:80502 Reymond"
print "     J:91257 Gray"
print "     J:93300 Blackshaw"
print ""

select distinct n.jnumID, n.accID, n.specimen
from #missingimage m, #noimage n
where n._Specimen_key = m._Specimen_key
order by n.numericPart, n.accID
go

