set nocount on
go

select distinct m.symbol "Symbol", h1.creation_date, h1._Refs_key, ha._Assay_key
into #homology
from MRK_Marker m, HMD_Homology h1, MRK_Homology_Cache hm1, MRK_Homology_Cache hm2, HMD_Homology_Assay ha
where m._Organism_key = 40
and m._Marker_Type_key = 1
and hm1._Marker_key = m._Marker_key
and hm1._Homology_key = h1._Homology_key
and hm1._Class_key = hm2._Class_key
and hm1._Homology_key = ha._Homology_key
and ha._Assay_key in (4,5)
and hm2._Organism_key != 40
and not exists (select 1 from MRK_ACC_View a
where m._Marker_key = a._Object_key
and a._LogicalDB_Key in (9, 13, 27))
go

set nocount off
go

print ""
print "Rat Genes with no GenBank, RefSeq or SwissProt Sequence ID but with Orthology"
print "using either Amino Acid or Nucleotide Sequence Comparison Assays"
print "(sorted by creation date, symbol)"
print ""

select distinct h.symbol "Symbol", a.abbrev "Assay", b.jnumID "J#", 
h.creation_date "Homology Creation Date"
from #homology h, HMD_Assay a, BIB_All_View b
where h._Assay_key = a._Assay_key
and h._Refs_key = b._Refs_key
order by h.creation_date desc, h.symbol
go

