
set nocount on
go

select a._Term_key, a._Object_key, a._Qualifier_key, e._EvidenceTerm_key, e._Refs_key
into #a
from VOC_Annot a, VOC_Evidence e
where a._AnnotType_key = 1000
and a._Annot_key = e._Annot_key
go

select a.*
into #dup
from #a a
group by _Term_key, _Object_key, _Qualifier_key, _EvidenceTerm_key, _Refs_key
having count(*) > 1
go

set nocount off
go

print ""
print "Duplicate GO Annotations"
print ""

select m.symbol, substring(t.term,1,50) 
from #dup d, MRK_Marker m, VOC_Term t
where d._Object_key = m._Marker_key
and d._Term_key = t._Term_key
order by m.symbol
go

