
print ""
print "Obsolete Gene Models associated with Markers"
print ""
print "This report lists Markers that have an association to NCBI Gene Model (ldb 59) but have no association to Entrez Gene (ldb 55)"
print ""

select distinct smc.accID as "NCBI Gene Model", a.accID as "MGI ID", m.symbol
from SEQ_Marker_Cache smc, ACC_Accession a, MRK_Marker m
where smc._LogicalDB_key = 59
and a._MGIType_key = 2
and a.preferred = 1
and a._LogicalDB_key = 1
and a._Object_key = m._Marker_key
and smc._Marker_key = m._Marker_key
and not exists (select 1 from ACC_Accession aa 
                where aa._LogicalDB_key = 55 
                and aa._MGIType_key = 2
                and smc.accID = aa.accID)
order by m.symbol
go

