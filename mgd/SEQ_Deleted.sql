
/* delete Sequences */

select s._Sequence_key
INTO TEMPORARY TABLE deleted1
from SEQ_Sequence s
where s._SequenceStatus_key = 316343
;

create index deleted1_idx1 on deleted1(_Sequence_key)
;

/* their accession ids (primary and secondary) */

select a.accID, d._Sequence_key
INTO TEMPORARY TABLE deleted2
from deleted1 d, ACC_Accession a
where d._Sequence_key = a._Object_key
and a._MGIType_key = 19
;

create index deleted2_idx1 on deleted2(accID)
;
create index deleted2_idx2 on deleted2(_Sequence_key)
;

/* deleted sequences annotated to mouse markers */

select d.accID as seqID, ma2.accID as mgiID, m.symbol as name
INTO TEMPORARY TABLE mdeleted
from deleted2 d, SEQ_Marker_Cache ma, ACC_Accession ma2, MRK_Marker m
where d._Sequence_key = ma._Sequence_key
and ma._Marker_key = ma2._Object_key 
and ma2._MGIType_key = 2
and ma2._LogicalDB_key = 1
and ma2.prefixPart = 'MGI:'
and ma2.preferred = 1
and ma._Marker_key = m._Marker_key 
;

create index mdeleted_idx1 on mdeleted(seqID)
;

/* deleted sequences annotated to molecular segments */

select d.accID as seqID, pa2.accID as mgiID, p.name
INTO TEMPORARY TABLE pdeleted
from deleted2 d, SEQ_Probe_Cache pa, ACC_Accession pa2, PRB_Probe p
where d._Sequence_key = pa._Sequence_key
and pa._Probe_key = pa2._Object_key
and pa2._MGIType_key = 3
and pa2._LogicalDB_key = 1
and pa2.prefixPart = 'MGI:'
and pa2.preferred = 1
and pa._Probe_key = p._Probe_key
;

create index pdeleted_idx1 on pdeleted(seqID)
;

\echo ''
\echo '    Deleted Sequences with MGI Associations'
\echo ''
\echo 'A row in this report represents a Sequence that is designated as Deleted'
\echo 'by the Sequence provider and contains associations to Marker and/or Molecular Segment.'
\echo ''
\echo 'Includes: all marker statuses (official, withdrawn)'
\echo 'Includes: all marker types (gene, DNA segment, etc.)'
\echo ''

\echo 'Markers'
select seqID, mgiID, name from mdeleted order by name, seqID;

\echo 'Probes'
select seqID, mgiID, name from pdeleted order by name, seqID;

