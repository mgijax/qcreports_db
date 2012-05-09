set nocount on
go

select a.accID, a._Object_key, t.term 
into #obsolete 
from VOC_Term_ACC_View a, VOC_Term t 
where t._Vocab_key = 5 
and t.isObsolete = 1 
and t._Term_key = a._Object_key
and a._LogicalDB_key = 34
and a.preferred = 1
go

create clustered index idx_key on #obsolete(_Object_key)
go

set nocount off
go

print ""
print "Genotype Annotations to Obsolete MP Terms"
print ""

select g.accID as "Genotype ID", o.accID as "MP ID", substring(o.term , 1, 100) as "Term"
from #obsolete o, VOC_Annot a, ACC_Accession g
where a._AnnotType_key = 1002 
and a._Term_key = o._Object_key 
and a._Object_key = g._Object_key 
and g._MGIType_key = 12
and g._LogicalDB_key = 1 
and g.prefixPart = "MGI:" 
and g.preferred = 1
go

drop table #obsolete 
go

