
set nocount on
go

/* select all Sequences which are annotated to Markers or Molecular Segments */

select sa._Object_key
into #seqs1
from ACC_Accession sa, ACC_Accession ma
where sa._MGIType_key = 19
and sa.accID = ma.accID
and ma._MGIType_key = 2
go

select sa._Object_key
into #seqs2
from ACC_Accession sa, ACC_Accession ma
where sa._MGIType_key = 19
and sa.accID = ma.accID
and ma._MGIType_key = 3
go

select _Object_key
into #seqs3
from #seqs1
union
select _Object_key
from #seqs2
go

create nonclustered index idx_obj on #seqs3(_Object_key)
go

/* select all Sequence References */

select r._Object_key, r._Refs_key
into #refs1
from #seqs3 s, MGI_Reference_Assoc r
where s._Object_key = r._Object_key
and r._MGIType_key = 19
go

create nonclustered index idx_refs on #refs1(_Refs_key)
go

/* select all Sequence References which are not associated with any other MGI Object */

/* there a 16 table limit, so let's break this up */

select r._Object_key, r._Refs_key
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

create nonclustered index idx_refs on #refs2(_Refs_key)
go

create nonclustered index idx_obj on #refs2(_Object_key)
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

select seqID = a1.accID, jnumID = a2.accID
from #refs2 r, ACC_Accession a1, ACC_Accession a2
where r._Object_key = a1._Object_key
and a1._MGIType_key = 19
and a1.preferred = 1
and r._Refs_key = a2._Object_key
and a2._MGIType_key = 1
and a2._LogicalDB_key = 1
and a2.prefixPart = "J:"
order by a2.accID
go

