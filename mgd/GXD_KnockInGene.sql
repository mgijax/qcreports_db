set nocount on
go

select a._Assay_key, a._Refs_key, specimenLabel = s.substring(specimenLabel, 1, 50)
into #knockin
from GXD_Assay a, GXD_Specimen s
where a._AssayType_key = 9
and a._Assay_key = s._Assay_key
and not exists (select 1 from GXD_AlleleGenotype g
where s._Genotype_key = g._Genotype_key
and a._Marker_key = g._Marker_key)
go

set nocount off
go

print ""
print "GXD Knock Ins where the assayed Gene is not the Gene which is mutated in the Genotype"
print ""

select a.accID "Assay", b.accID "J:", k.specimenLabel
from #knockin k, GXD_Assay_Acc_View a, BIB_Acc_View b
where k._Assay_key = a._Object_key
and k._Refs_key = b._Object_key
and b._LogicalDB_key = 1
and b.prefixPart = "J:"
go

