
/* GO Annotations to unknown terms */
/* only include non-FANTOM references */
/* and J: creation date >= Annotation creation date */

select distinct substring(m.symbol,1,25) as symbol, m._Marker_key, r._Refs_key,
substring(r.jnumID,1,20) as jnumID,
substring(r.pubmedID,1,20) as pubmedID, 
convert(char(10), rr.creation_date, 101) as jnumDate,
convert(char(10), a.creation_date, 101) as annotDate
into #temp1
from MRK_Marker m, VOC_Annot_View a, MRK_Reference r, BIB_Refs rr
where m._Organism_key = 1 
and m._Marker_key = a._Object_key 
and a._AnnotType_key = 1000 
and a.accID in ('GO:0008150', 'GO:0003674', 'GO:0005575') 
and m._Marker_key = r._Marker_key
and r.pubmedID not in ('11217851', '12466851', '14621295', '11125038', '12466854', '12466855', '12693553')
and r._Refs_key = rr._Refs_key
and rr.creation_date >= a.creation_date
go

create index temp1_idx1 on #temp1(_Marker_key)
go
create index temp1_idx2 on #temp1(_Refs_key)
go

/* grab the marker accession ids */

select t._Marker_key, t.symbol, t._Refs_key, t.jnumID, t.pubmedID, jnumDate, annotDate, substring(ma.accID,1,20) as mgiID
into #temp2
from #temp1 t, ACC_Accession ma
where t._Marker_key = ma._Object_key 
and ma._MGIType_key = 2 
and ma.prefixPart = 'MGI:' 
and ma._LogicalDB_key = 1 
and ma.preferred = 1 
go

create index temp2_idx1 on #temp2(_Marker_key)
go
create index temp2_idx2 on #temp2(_Refs_key)
go

/* set OMIM yes/no flag */

select distinct t._Marker_key, t.symbol
into #omim
from #temp2 t, VOC_Annot va,
GXD_AlleleGenotype agt, VOC_Term vt, ALL_Allele a
where t._Marker_key = agt._Marker_key
and va._AnnotType_key = 1005
and va._Term_key = vt._Term_key
and vt.isObsolete = 0
and va._Qualifier_key in (1614158)
and va._Object_key = agt._Genotype_key
and agt._Allele_key = a._Allele_key
and a._Allele_Status_key != 847112
and a.isWildType != 1
go

create index omim_idx1 on #omim(_Marker_key)
go

/* grab the pubmed ids */
/* tag 1: for those with GO annotations only */
/* tag 2: for those with GO and A&P annotations only */
/* tag 3: any GO annotations */
/* for those without GO annotations */

/* tag 1: for those with GO annotations only */
select t._Marker_key, t.symbol, t.mgiID, t.jnumID, t.pubmedID, t.jnumDate, t.annotDate, '1' as tag
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
select t._Marker_key, t.symbol, t.mgiID, t.jnumID, t.pubmedID, t.jnumDate, t.annotDate, '2' as tag
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
select t._Marker_key, t.symbol, t.mgiID, t.jnumID, t.pubmedID, t.jnumDate, t.annotDate, '3' as tag
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

create index temp3_idx1 on #temp3(_Marker_key)
go

/* set hasOMIM */

select t.*, 'Y' as hasOMIM
into #temp4
from #temp3 t
where exists (select 1 from #omim o where t._Marker_key = o._Marker_key)
go

insert into #temp4
select t.*, 'N' as hasOMIM
from #temp3 t
where not exists (select 1 from #omim o where t._Marker_key = o._Marker_key)
go

create index temp4_idx1 on #temp4(symbol)
go
create index temp4_idx2 on #temp4(tag)
go

\echo ''
\echo 'All genes with ''unknown'' annotations with new indexed literature'
\echo '(J: creation date >= Annotation creation date)'
\echo 'and if reference is selected for GO and ''not used'' for any GO annotation'
\echo '(excludes FANTOM papers 11217851 and 12466851, and 14621295, 11125038, 12466854, 12466855, and 12693553)'

select 'Number of unique MGI Gene IDs:  ', count(distinct mgiID) from #temp4
union
select 'Number of unique MGI Gene IDs associated with OMIM:', count(distinct mgiID) from #temp4 where hasOMIM = 'Y'
union
select 'Number of total rows:  ', count(*) from #temp4
go

\echo ''
\echo ' tag 1 = only for GO'
\echo ' tag 2 = only for GO and AP'
\echo ' tag 3 = any GO'
\echo ''

select distinct symbol, mgiID, jnumID, pubmedID, tag, hasOMIM, jnumDate, annotDate
from #temp4 
order by symbol, tag
go

