
-- GO Annotations to unknown terms 
-- only include non-FANTOM references 
-- and J: creation date >= Annotation creation date 
-- ('GO:0008150', 'GO:0003674', 'GO:0005575')

select distinct substring(m.symbol,1,25) as symbol, m._Marker_key, r._Refs_key,
substring(r.jnumID,1,20) as jnumID,
substring(r.pubmedID,1,20) as pubmedID, 
to_char(rr.creation_date, 'MM/dd/yyyy') as jnumDate,
to_char(a.creation_date, 'MM/dd/yyyy') as annotDate
INTO TEMPORARY TABLE temp1
from MRK_Marker m, VOC_Annot a, MRK_Reference r, BIB_Refs rr
where m._Organism_key = 1 
and m._Marker_key = a._Object_key 
and a._AnnotType_key = 1000 
and a._Term_key in (1098,120,6113)
and m._Marker_key = r._Marker_key
and r.pubmedID not in ('11217851', '12466851', '14621295', '11125038', '12466854', '12466855', '12693553')
and r._Refs_key = rr._Refs_key
and rr.creation_date >= a.creation_date
;

create index temp1_idx1 on temp1(_Marker_key)
;
create index temp1_idx2 on temp1(_Refs_key)
;

-- grab the marker accession ids

select t._Marker_key, t.symbol, t._Refs_key, t.jnumID, t.pubmedID, jnumDate, annotDate, substring(ma.accID,1,20) as mgiID
INTO TEMPORARY TABLE temp2
from temp1 t, ACC_Accession ma
where t._Marker_key = ma._Object_key 
and ma._MGIType_key = 2 
and ma.prefixPart = 'MGI:' 
and ma._LogicalDB_key = 1 
and ma.preferred = 1 
;

create index temp2_idx1 on temp2(_Marker_key)
;
create index temp2_idx2 on temp2(_Refs_key)
;

-- set DO yes/no flag

select distinct t._Marker_key, t.symbol
INTO TEMPORARY TABLE diseaseontology
from temp2 t, VOC_Annot va,
GXD_AlleleGenotype agt, VOC_Term vt, ALL_Allele a
where t._Marker_key = agt._Marker_key
and va._AnnotType_key = 1020
and va._Term_key = vt._Term_key
and vt.isObsolete = 0
and va._Qualifier_key in (1614158)
and va._Object_key = agt._Genotype_key
and agt._Allele_key = a._Allele_key
and a._Allele_Status_key != 847112
and a.isWildType != 1
;

create index diseaseontology_idx1 on diseaseontology(_Marker_key)
;

-- grab the pubmed ids
-- tag 1: for those with GO annotations only
-- tag 2: for those with GO and A&P annotations only 
-- tag 3: any GO annotations
-- for those without GO annotations

-- tag 1: for those with GO annotations only
-- group GO, Routed/Chosen

--select t._Marker_key, t.symbol, t.mgiID, t.jnumID, t.pubmedID, t.jnumDate, t.annotDate, '1'::text as tag
--INTO TEMPORARY TABLE temp3
--from temp2 t
--where exists (select 1 from BIB_DataSet_Assoc a, BIB_DataSet d
--where t._Refs_key = a._Refs_key
--and a._DataSet_key = d._DataSet_key
--and d.abbreviation = 'GO'
--and a.isNeverUsed = 0)
--and not exists (select 1 from BIB_DataSet_Assoc a, BIB_DataSet d
--where t._Refs_key = a._Refs_key
--and a._DataSet_key = d._DataSet_key
--and d.abbreviation != 'GO'
--and a.isNeverUsed = 0)
--and not exists (select 1 from VOC_Annot va, VOC_Evidence e
--where va._AnnotType_key = 1000
--and va._Annot_key = e._Annot_key
--and e._Refs_key = t._Refs_key)
--;
select t._Marker_key, t.symbol, t.mgiID, t.jnumID, t.pubmedID, t.jnumDate, t.annotDate, '1'::text as tag
INTO TEMPORARY TABLE temp3
from temp2 t
where exists (select 1 from BIB_Workflow_Status s
	where t._Refs_key = s._Refs_key
	and s._Group_key = 31576666
	and s._Status_key in (31576670,31576671)
	and s.isCurrent = 1)
and not exists (select 1 from BIB_Workflow_Status s
	where t._Refs_key = s._Refs_key
	and s._Group_key != 31576666
	and s._Status_key in (31576670,31576671)
	and s.isCurrent = 1)
and not exists (select 1 from VOC_Annot va, VOC_Evidence e
	where va._AnnotType_key = 1000
	and va._Annot_key = e._Annot_key
	and e._Refs_key = t._Refs_key)
;

-- tag 2: for those with GO and A&P annotations only
-- group GO, Routed/Chosen
-- group AP, Routed/Chosen
-- and not in tag 1

--INSERT INTO temp3
--select t._Marker_key, t.symbol, t.mgiID, t.jnumID, t.pubmedID, t.jnumDate, t.annotDate, '2'::text as tag
--from temp2 t
--where not exists (select 1 from temp3 t3 
--where t.symbol = t3.symbol
--and t.pubmedID = t3.pubmedID)
--and exists (select 1 from BIB_DataSet_Assoc a, BIB_DataSet d
--where t._Refs_key = a._Refs_key
--and a._DataSet_key = d._DataSet_key
--and d.abbreviation = 'GO'
--and a.isNeverUsed = 0)
--and exists (select 1 from BIB_DataSet_Assoc a, BIB_DataSet d
--where t._Refs_key = a._Refs_key
--and a._DataSet_key = d._DataSet_key
--and d.abbreviation = 'Allele/Pheno'
--and a.isNeverUsed = 0)
--and not exists (select 1 from BIB_DataSet_Assoc a, BIB_DataSet d
--where t._Refs_key = a._Refs_key
--and a._DataSet_key = d._DataSet_key
--and d.abbreviation not in ('GO', 'Allele/Pheno')
--and a.isNeverUsed = 0)
--and not exists (select 1 from VOC_Annot va, VOC_Evidence e
--where va._AnnotType_key = 1000
--and va._Annot_key = e._Annot_key
--and e._Refs_key = t._Refs_key)
--;

INSERT INTO temp3
select t._Marker_key, t.symbol, t.mgiID, t.jnumID, t.pubmedID, t.jnumDate, t.annotDate, '2'::text as tag
from temp2 t
where not exists (select 1 from temp3 t3 
	where t.symbol = t3.symbol
	and t.pubmedID = t3.pubmedID)
and exists (select 1 from BIB_Workflow_Status s
	where t._Refs_key = s._Refs_key
	and s._Group_key = 31576666
	and s._Status_key in (31576670,31576671)
	and s.isCurrent = 1)
and exists (select 1 from BIB_Workflow_Status s
	where t._Refs_key = s._Refs_key
	and s._Group_key = 31576664
	and s._Status_key in (31576670,31576671)
	and s.isCurrent = 1)
and not exists (select 1 from BIB_Workflow_Status s
	where t._Refs_key = s._Refs_key
	and s._Group_key in (31576666, 31576664)
	and s._Status_key in (31576670,31576671)
	and s.isCurrent = 1)
and not exists (select 1 from VOC_Annot va, VOC_Evidence e
	where va._AnnotType_key = 1000
	and va._Annot_key = e._Annot_key
	and e._Refs_key = t._Refs_key)
;

-- tag 3: any GO annotations 
-- and not in tag 1 or 2

--INSERT INTO temp3
--select t._Marker_key, t.symbol, t.mgiID, t.jnumID, t.pubmedID, t.jnumDate, t.annotDate, '3'::text as tag
--from temp2 t
--where not exists (select 1 from temp3 t3 
--where t.symbol = t3.symbol
--and t.pubmedID = t3.pubmedID)
--and exists (select 1 from BIB_DataSet_Assoc a, BIB_DataSet d
--where t._Refs_key = a._Refs_key
--and a._DataSet_key = d._DataSet_key
--and d.abbreviation = 'GO'
--and a.isNeverUsed = 0)
--and not exists (select 1 from VOC_Annot va, VOC_Evidence e
--where va._AnnotType_key = 1000
--and va._Annot_key = e._Annot_key
--and e._Refs_key = t._Refs_key)
--;

INSERT INTO temp3
select t._Marker_key, t.symbol, t.mgiID, t.jnumID, t.pubmedID, t.jnumDate, t.annotDate, '3'::text as tag
from temp2 t
where not exists (select 1 from temp3 t3 
	where t.symbol = t3.symbol
	and t.pubmedID = t3.pubmedID)
and exists (select 1 from BIB_Workflow_Status s
	where t._Refs_key = s._Refs_key
	and s._Group_key = 31576666
	and s._Status_key in (31576670,31576671)
	and s.isCurrent = 1)
and not exists (select 1 from VOC_Annot va, VOC_Evidence e
	where va._AnnotType_key = 1000
	and va._Annot_key = e._Annot_key
	and e._Refs_key = t._Refs_key)
;

create index temp3_idx1 on temp3(_Marker_key)
;

-- set hasDO

select t.*, 'Y'::text as hasDO
INTO TEMPORARY TABLE temp4
from temp3 t
where exists (select 1 from diseaseontology o where t._Marker_key = o._Marker_key)
;

INSERT INTO temp4
select t.*, 'N'::text as hasDO
from temp3 t
where not exists (select 1 from diseaseontology o where t._Marker_key = o._Marker_key)
;

create index temp4_idx1 on temp4(symbol)
;
create index temp4_idx2 on temp4(tag)
;

\echo ''
\echo 'All genes with ''unknown'' annotations with new indexed literature'
\echo '(J: creation date >= Annotation creation date)'
\echo 'and if reference is selected for GO and ''not used'' for any GO annotation'
\echo '(excludes FANTOM papers 11217851 and 12466851, and 14621295, 11125038, 12466854, 12466855, and 12693553)'

select 'Number of unique MGI Gene IDs:  ', count(distinct mgiID) from temp4
union
select 'Number of unique MGI Gene IDs associated with DO:', count(distinct mgiID) from temp4 where hasDO = 'Y'
union
select 'Number of total rows:  ', count(*) from temp4
;

\echo ''
\echo ' tag 1 = only for GO'
\echo ' tag 2 = only for GO and AP'
\echo ' tag 3 = any GO'
\echo ''

select distinct symbol, mgiID, jnumID, pubmedID, tag, hasDO, jnumDate, annotDate
from temp4 
order by symbol, tag
;

