set nocount on
go

select distinct m.symbol "Symbol", substring(s.status,1,10) "Status", h1.creation_date, h1._Refs_key, ha._Assay_key
into #homology
from MRK_Marker m, MRK_Status s, 
HMD_Homology h1, MRK_Homology_Cache hm1, MRK_Homology_Cache hm2, HMD_Homology_Assay ha
where m._Organism_key = 1
and m._Marker_Type_key = 1
and m._Marker_Status_key = s._Marker_Status_key
and hm1._Marker_key = m._Marker_key
and hm1._Homology_key = h1._Homology_key
and hm1._Class_key = hm2._Class_key
and hm1._Homology_key = ha._Homology_key
and ha._Assay_key in (4,5)
and hm2._Organism_key = 2
and not exists (select 1 from MRK_ACC_View a
where m._Marker_key = a._Object_key
and a._LogicalDB_Key in (9, 27))
go

set nocount off
go

print ""
print "Mouse Genes with no Sequence ID but with Human Orthology"
print ""

select distinct h.symbol "Symbol", substring(h.status,1,10) "Status", a.abbrev "Assay", b.jnumID "J#", 
h.creation_date "Orthology Creation Date"
from #homology h, HMD_Assay a, BIB_All_View b
where h._Assay_key = a._Assay_key
and h._Refs_key = b._Refs_key
order by h.creation_date desc, h.symbol
go

