
print ""
print "References which have GXD Annotations to 'Not Applicable' Genotype (MGI:2166309)"
print ""

select b.accID
from ACC_Accession a, GXD_Expression ge, GXD_Assay ga, BIB_Acc_View b
where a.accID = "MGI:2166309"
and a._Object_key = ge._Genotype_key
and ge._Assay_key = ga._Assay_key
and ga._Refs_key = b._Object_key
and b.prefixPart = "J:"
go
