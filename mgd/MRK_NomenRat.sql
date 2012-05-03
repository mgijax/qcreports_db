set nocount on
go

select distinct r._Marker_key, r._Current_key, r.symbol, r.current_symbol
into #markers
from MRK_History h, MRK_Current_View r, HMD_Homology_Marker hm
where h._Marker_Event_key in (2,3,4,5)
and h._History_key = r._Marker_key
and r._Current_key = hm._Marker_key
go

set nocount off
go

print ''
print 'Mouse Symbols with nomenclature changes which contain Rat homologs with unofficial nomenclature'
print '(meaning the Rat symbol has no EntrezGene ID)'
print ''

select distinct m.current_symbol as 'New Mouse Symbol', m2.symbol as 'Rat Symbol'
from #markers m, 
MRK_Homology_Cache hm1, MRK_Homology_Cache hm2, MRK_Marker m2
where m._Current_key = hm1._Marker_key
and hm1._Class_key = hm2._Class_key
and hm2._Organism_key = 40
and hm2._Marker_key = m2._Marker_key
and m2.symbol != m.current_symbol
and not exists (select 1 from ACC_Accession ma 
where m2._Marker_key = ma._Object_key
and ma._MGIType_key = 2
and ma._LogicalDB_key = 55)
order by m.current_symbol
go

