set nocount on
go

/* Select all classes where at least one homology has an Unreviewed Assay */

select distinct _Class_key
into #class
from HMD_Homology h, HMD_Homology_Assay a
where h._Homology_key = a._Homology_key
and a._Assay_key = 15
go

/* Select the Unreviewed homologies for the classes */

select distinct h._Homology_key, h._Class_key, m._Marker_key
into #homology
from #class c, HMD_Homology h, HMD_Homology_Marker m, HMD_Homology_Assay a, MRK_Marker mm
where c._Class_key = h._Class_key
and h._Homology_key = m._Homology_key
and h._Homology_key = a._Homology_key
and a._Assay_key = 15
and m._Marker_key = mm._Marker_key
and mm._Species_key in (1,2,9,11,35,40,44)
go

set nocount off
go

print ""
print "Homologies for Oxford Grid Species w/ Unreviewed Assay"
print ""

select r.jnumID, r.symbol, r.commonName, a.assay
from #homology s, HMD_Homology_View r, HMD_Homology_Assay_View a
where s._Homology_key = r._Homology_key
and r._Homology_key = a._Homology_key
order by r.jnum, s._Homology_key
go
 
