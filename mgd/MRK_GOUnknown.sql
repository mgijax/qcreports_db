
set nocount on
go

/* GO Annotations to unknown terms */

select distinct symbol = substring(m.symbol,1,25), m._Marker_key, r._Refs_key
into #temp1
from MRK_Marker m, VOC_Annot_View a, MRK_Reference r
where m._Organism_key = 1 
and m._Marker_key = a._Object_key 
and a._AnnotType_key = 1000 
and a.accID in ("GO:0000004", "GO:0008372", "GO:0005554") 
and m._Marker_key = r._Marker_key
go

create index idx1 on #temp1(_Marker_key)
go

create index idx2 on #temp1(_Refs_key)
go

/* only include non-FANTOM references */

select t.symbol, t._Refs_key, mgiID = substring(ma.accID,1,20), pubMedID = substring(ba.accID, 1, 20)
into #temp2
from #temp1 t, ACC_Accession ma, ACC_Accession ba
where t._Marker_key = ma._Object_key 
and ma._MGIType_key = 2 
and ma.prefixPart = "MGI:" 
and ma._LogicalDB_key = 1 
and ma.preferred = 1 
and t._Refs_key = ba._Object_key 
and ba._MGIType_key = 1 
and ba._LogicalDB_key = 29
and ba.accID not in ('11217851', '12466851')
go

create index idx1 on #temp2(_Refs_key)
go

set nocount off
go

print ""
print "All genes with 'unknown' annotations with new indexed literature"
print "Indicator column indicates if reference is selected for GO and 'not used' for any GO annotation"
print "(excludes FANTOM papers 11217851 and 12466851)"
print ""

/* set indicator if reference is selected for GO and 'not used' for any GO annotation */
/* else set indicator to blank */

select t.symbol, t.mgiID, t.pubMedID, indicator = "Y"
from #temp2 t, BIB_DataSet_Assoc a, BIB_DataSet d
where t._Refs_key = a._Refs_key
and a._DataSet_key = d._DataSet_key
and d.abbreviation = 'GO'
and a.isNeverUsed = 0
and not exists (select 1 from VOC_Annot va, VOC_Evidence e
where va._AnnotType_key = 1000
and va._Annot_key = e._Annot_key
and e._Refs_key = t._Refs_key)
union
select t.symbol, t.mgiID, t.pubMedID, indicator = ""
from #temp2 t
where not exists (select 1 from BIB_DataSet_Assoc a, BIB_DataSet d
where t._Refs_key = a._Refs_key
and a._DataSet_key = d._DataSet_key
and d.abbreviation = 'GO'
and not exists (select 1 from VOC_Annot va, VOC_Evidence e
where va._AnnotType_key = 1000
and va._Annot_key = e._Annot_key
and e._Refs_key = t._Refs_key))
order by t.symbol
go
