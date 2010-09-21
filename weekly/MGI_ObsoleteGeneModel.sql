
print ""
print "Obsolete Gene Models associated with Markers"
print ""
print "This report lists Markers that have an association to NCBI Gene Model (ldb 59)"
print "but have no association to Entrez Gene (ldb 55)"
print ""

select a.accID, ma.accID, m.symbol
from MRK_Marker m, ACC_Accession a, ACC_Accession ma
where a._MGIType_key = 2
and a._LogicalDB_key = 59
and a._Object_key = m._Marker_key
and m._Organism_key = 1
and a._Object_key = ma._Object_key
and ma._MGIType_key = 2
and ma._LogicalDB_key = 1
and ma.preferred = 1
and not exists (select 1 from ACC_Accession aa
where a._Object_key = aa._Object_key
and aa._MGIType_key = 2
and aa._LogicalDB_key = 55)
order by m.symbol
go

