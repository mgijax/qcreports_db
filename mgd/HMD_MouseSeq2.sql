set nocount on
go

select distinct m.symbol "Symbol", h1.creation_date, h1._Refs_key, ha._Assay_key
into #homology
from MRK_Marker m, HMD_Homology h1, HMD_Homology_Marker hm1, 
HMD_Homology h2, HMD_Homology_Marker hm2,
HMD_Homology_Assay ha, MRK_Marker m2
where m._Species_key = 1
and m._Marker_Type_key = 1
and hm1._Marker_key = m._Marker_key
and hm1._Homology_key = h1._Homology_key
and h1._Class_key = h2._Class_key
and h2._Homology_key = hm2._Homology_key
and hm1._Homology_key = ha._Homology_key
and ha._Assay_key in (4,5)
and hm2._Marker_key = m2._Marker_key
and m2._Species_key = 2
and not exists (select 1 from MRK_ACC_View a
where m._Marker_key = a._Object_key
and a._LogicalDB_Key = 9)
go

set nocount off
go

print ""
print "Mouse Genes with no Sequence ID but with Human Homology"
print ""

select distinct h.symbol "Symbol", a.abbrev "Assay", b.jnumID "J#", 
h.creation_date "Homology Creation Date"
from #homology h, HMD_Assay a, BIB_All_View b
where h._Assay_key = a._Assay_key
and h._Refs_key = b._Refs_key
order by h.creation_date, h.symbol
go

