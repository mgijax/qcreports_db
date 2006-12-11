
set nocount on
go

print ""
print "PIRSFLoad - Superfamilies not mapped to MGI
print ""

select a.accID "Superfamily ID", substring(p.term,1,50) "Superfamily Name"
from VOC_Term p, ACC_Accession a
where p._Vocab_key = 46 
and not exists (select 1 from VOC_Annot a where p._Term_key = a._Term_key and a._AnnotType_key = 1007)
and p._Term_key = a._Object_key
and a._MGIType_key = 13
order by a.accID
go


