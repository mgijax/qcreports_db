set nocount on
go

/* Select all classes where at least one homology has Assay of */
/* nucleotide sequence similiarity or amino acid sequence similarity */

select distinct _Class_key
into #class
from HMD_Homology h, HMD_Homology_Assay a
where h._Homology_key = a._Homology_key
and a._Assay_key in (4,5)
go

/* Select the mouse homologies for the classes */
/* where the mouse gene has no seq ID */

select distinct m._Homology_key, m._Class_key, m._Marker_key
into #homology
from #class c, MRK_Homology_Cache m, HMD_Homology_Assay a
where c._Class_key = m._Class_key
and m._Homology_key = a._Homology_key
and a._Assay_key in (4,5)
and m._Organism_key = 1
and not exists (select 1 from ACC_Accession a
where m._Marker_key = a._Object_key
and a._MGIType_key = 2
and a._LogicalDB_key in (9, 27))
go

set nocount off
go

print ""
print "Mouse Markers in Orthology w/ Nucleotide or Amino Acid Sequence Similarity Assay"
print "and Marker has no Seq ID"
print ""

select distinct r.jnumID, s._Class_key, r.symbol
from #homology s, HMD_Homology_View r, HMD_Homology_Assay_View a
where s._Homology_key = r._Homology_key
and s._Marker_key = r._Marker_key
and r._Homology_key = a._Homology_key
order by r.jnum, r.symbol
go
 
