
set nocount on
go

/* GO Annotations to unknown terms */
/* only include non-FANTOM references */

select distinct substring(m.symbol,1,25) as symbol, m._Marker_key, r._Refs_key, 
substring(r.pubmedID,1,20) as pubmedID
into #temp1
from MRK_Marker m, VOC_Annot_View a, MRK_Reference r
where m._Organism_key = 1 
and m._Marker_key = a._Object_key 
and a._AnnotType_key = 1000 
and a.accID in ('GO:0008150', 'GO:0003674', 'GO:0005575') 
and m._Marker_key = r._Marker_key
and r.pubmedID not in ('11217851', '12466851', '14621295', '11125038', '12466854', '12466855', '12693553')
go

create index idx1 on #temp1(_Marker_key)
go

create index idx2 on #temp1(_Refs_key)
go

/* grab the marker accession ids */

select t.symbol, t._Refs_key, t.pubmedID, substring(ma.accID,1,20) as mgiID
into #temp2
from #temp1 t, ACC_Accession ma
where t._Marker_key = ma._Object_key 
and ma._MGIType_key = 2 
and ma.prefixPart = 'MGI:' 
and ma._LogicalDB_key = 1 
and ma.preferred = 1 
go

create index idx1 on #temp2(_Refs_key)
go

/* grab the pubmed ids */
/* tag 1: for those with GO annotations only */
/* tag 2: for those with GO and A&P annotations only */
/* tag 3: any GO annotations */
/* for those without GO annotations */

/* tag 1: for those with GO annotations only */
select t.symbol, t.mgiID, t.pubmedID, '1' as tag
into #temp3
from #temp2 t
where exists (select 1 from BIB_DataSet_Assoc a, BIB_DataSet d
where t._Refs_key = a._Refs_key
and a._DataSet_key = d._DataSet_key
and d.abbreviation = 'GO'
and a.isNeverUsed = 0)
and not exists (select 1 from BIB_DataSet_Assoc a, BIB_DataSet d
where t._Refs_key = a._Refs_key
and a._DataSet_key = d._DataSet_key
and d.abbreviation != 'GO'
and a.isNeverUsed = 0)
and not exists (select 1 from VOC_Annot va, VOC_Evidence e
where va._AnnotType_key = 1000
and va._Annot_key = e._Annot_key
and e._Refs_key = t._Refs_key)
go

/* tag 2: for those with GO and A&P annotations only */
/* and not in tag 1 */
insert into #temp3
select t.symbol, t.mgiID, t.pubmedID, '2' as tag
from #temp2 t
where not exists (select 1 from #temp3 t3 
where t.symbol = t3.symbol
and t.pubmedID = t3.pubmedID)
and exists (select 1 from BIB_DataSet_Assoc a, BIB_DataSet d
where t._Refs_key = a._Refs_key
and a._DataSet_key = d._DataSet_key
and d.abbreviation = 'GO'
and a.isNeverUsed = 0)
and exists (select 1 from BIB_DataSet_Assoc a, BIB_DataSet d
where t._Refs_key = a._Refs_key
and a._DataSet_key = d._DataSet_key
and d.abbreviation = 'Allele/Pheno'
and a.isNeverUsed = 0)
and not exists (select 1 from BIB_DataSet_Assoc a, BIB_DataSet d
where t._Refs_key = a._Refs_key
and a._DataSet_key = d._DataSet_key
and d.abbreviation not in ('GO', 'Allele/Pheno')
and a.isNeverUsed = 0)
and not exists (select 1 from VOC_Annot va, VOC_Evidence e
where va._AnnotType_key = 1000
and va._Annot_key = e._Annot_key
and e._Refs_key = t._Refs_key)
go

/* tag 3: any GO annotations */
/* and not in tag 1 or 2 */
insert into #temp3
select t.symbol, t.mgiID, t.pubmedID, '3' as tag
from #temp2 t
where not exists (select 1 from #temp3 t3 
where t.symbol = t3.symbol
and t.pubmedID = t3.pubmedID)
and exists (select 1 from BIB_DataSet_Assoc a, BIB_DataSet d
where t._Refs_key = a._Refs_key
and a._DataSet_key = d._DataSet_key
and d.abbreviation = 'GO'
and a.isNeverUsed = 0)
and not exists (select 1 from VOC_Annot va, VOC_Evidence e
where va._AnnotType_key = 1000
and va._Annot_key = e._Annot_key
and e._Refs_key = t._Refs_key)
go

print ''
print 'All genes with ''unknown'' annotations with new indexed literature'
print 'and if reference is selected for GO and ''not used'' for any GO annotation'
print '(excludes FANTOM papers 11217851 and 12466851, and 14621295, 11125038, 12466854, 12466855, and 12693553)'

select 'Number of unique MGI Gene IDs:  ', count(distinct mgiID) from #temp3
union
select 'Number of total rows:  ', count(*) from #temp3
go

print ''
print ' tag 1 = only for GO'
print ' tag 2 = only for GO and AP'
print ' tag 3 = any GO'
print ''

set nocount off
go

select * from #temp3 order by tag, symbol
go

drop table #temp1
drop table #temp2
drop table #temp3
go

