
select a._Term_key, a._Object_key, a._Qualifier_key, e._EvidenceTerm_key, e._Refs_key
into #a
from VOC_Annot a, VOC_Evidence e
where a._AnnotType_key = 1002
and a._Annot_key = e._Annot_key
go

select a.*
into #dup
from #a a
group by _Term_key, _Object_key, _Qualifier_key, _EvidenceTerm_key, _Refs_key
having count(*) > 1
go

print ''
print 'Duplicate MP Annotations'
print ''

select a.accID, ta.accID, substring(t.term,1,50) as term
from #dup d, ACC_Accession a, ACC_Accession ta, VOC_Term t
where d._Object_key = a._Object_key
and a._MGIType_key = 12
and d._Term_key = ta._Object_key
and ta._MGIType_key = 13
and ta.preferred = 1
and d._Term_key = t._Term_key
order by ta.accID
go

