set nocount on
go

select a._Assay_key, a._Marker_key, p._Antibody_key
into #antibody
from GXD_Assay a, GXD_AntibodyPrep p
where a._AntibodyPrep_key = p._AntibodyPrep_key
and a._AssayType_key != 9
go

set nocount off
go

print ""
print "GXD Assay Antibody/Marker Pairs No Longer Found in Master Antibody Table"
print ""

select m.symbol "Marker", substring(b.antibodyName,1,75) "Antibody", a.accID "Assay"
from #antibody p, GXD_Antibody b, MRK_Marker m, ACC_Accession a
where p._Antibody_key = b._Antibody_key
and p._Marker_key = m._Marker_key
and p._Assay_key = a._Object_key
and a._MGIType_key = 8
and not exists (select 1 from GXD_AntibodyMarker bm
                where p._Antibody_key = bm._Antibody_key
                and p._Marker_key = bm._Marker_key)
go

