
set nocount on
go

/* Sequence IDs annotated to Molecular Segments */

select a.accID, a._LogicalDB_key
into #accs
from ACC_Accession a
where a._LogicalDB_key = 9
and a._MGIType_key = 3
go
create index idx1 on #accs(accID)
create index idx2 on #accs(_LogicalDB_key)
go
select distinct accID, _LogicalDB_key into #paccs from #accs
go
create index idx1 on #paccs(accID)
go
drop table #accs
go

/* Sequence IDs annotated to Genes */

select a.accID, a._LogicalDB_key
into #accs
from ACC_Accession a
where a._LogicalDB_key in (9,13,27,35,36,41,53)
and a._MGIType_key = 2
go
create index idx1 on #accs(accID)
create index idx2 on #accs(_LogicalDB_key)
go
select distinct accID, _LogicalDB_key into #maccs from #accs
go
create index idx1 on #maccs(accID)
go
drop table #accs
go

/* union to get one distinct set */

select accID, _LogicalDB_key into #accs from #paccs
union
select accID, _LogicalDB_key from #maccs
go
create index idx1 on #accs(accID)
go
drop table #paccids
go
drop table #maccids
go

/* retrieve object keys for acc ids */

select a.accID, s._Object_key
into #seqs
from #accs a, ACC_Accession s
where a.accID = s.accID
and s._MGIType_key = 19
and a._LogicalDB_key = s._LogicalDB_key
go
create index idx1 on #seqs(_Object_key)
go

/* select all Sequence References */

select s.accID, s._Object_key, r._Refs_key
into #refs1
from #seqs s, MGI_Reference_Assoc r
where s._Object_key = r._Object_key
and r._MGIType_key = 19
go

create index idx1 on #refs1(_Refs_key)
go

/* select all Sequence References which are not associated with any other MGI Object */

/* there a 16 table limit, so let's break this up */

select r.accID, r._Object_key, r._Refs_key
into #refs2
from #refs1 r
where not exists (select 1 from ACC_AccessionReference a where r._Refs_key = a._Refs_key)
and not exists (select 1 from ALL_Reference a where r._Refs_key = a._Refs_key)
and not exists (select 1 from ALL_Synonym a where r._Refs_key = a._Refs_key)
and not exists (select 1 from CRS_References a where r._Refs_key = a._Refs_key)
and not exists (select 1 from DAG_DAG a where r._Refs_key = a._Refs_key)
and not exists (select 1 from GXD_Antibody a where r._Refs_key = a._Refs_key)
and not exists (select 1 from GXD_AntibodyAlias a where r._Refs_key = a._Refs_key)
and not exists (select 1 from GXD_Assay a where r._Refs_key = a._Refs_key)
and not exists (select 1 from GXD_Index a where r._Refs_key = a._Refs_key)
and not exists (select 1 from HMD_Homology a where r._Refs_key = a._Refs_key)
and not exists (select 1 from IMG_Image a where r._Refs_key = a._Refs_key)
go

create index idx1 on #refs2(_Refs_key)
go

delete #refs2
from #refs2 r
where exists (select 1 from MLC_Reference a where r._Refs_key = a._Refs_key)
or exists (select 1 from MLD_Expts a where r._Refs_key = a._Refs_key)
or exists (select 1 from MLD_Marker a where r._Refs_key = a._Refs_key)
or exists (select 1 from MLD_Notes a where r._Refs_key = a._Refs_key)
or exists (select 1 from MRK_Reference a where r._Refs_key = a._Refs_key)
or exists (select 1 from NOM_Synonym a where r._Refs_key = a._Refs_key)
or exists (select 1 from PRB_Marker a where r._Refs_key = a._Refs_key)
or exists (select 1 from PRB_Reference a where r._Refs_key = a._Refs_key)
or exists (select 1 from PRB_Source a where r._Refs_key = a._Refs_key)
or exists (select 1 from RI_Summary_Expt_Ref a where r._Refs_key = a._Refs_key)
or exists (select 1 from VOC_Evidence a where r._Refs_key = a._Refs_key)
or exists (select 1 from VOC_Vocab a where r._Refs_key = a._Refs_key)
go

set nocount off
go

/* exclude J:68324? (RIKEN) */

print ""
print "References Associated with a Sequence but no other MGI Object"
print ""

select seqID = r.accID, jnumID = a1.accID
from #refs2 r, ACC_Accession a1
where r._Refs_key = a1._Object_key
and a1._MGIType_key = 1
and a1._LogicalDB_key = 1
and a1.prefixPart = "J:"
order by a1.accID
go

