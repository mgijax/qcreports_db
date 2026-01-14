select p._Probe_key, p.name 
INTO TEMPORARY TABLE probes
from PRB_Probe p
where not exists (select r.* from PRB_Reference r where p._Probe_key = r._Probe_key)
;

select distinct pp._Probe_key, pr._Refs_key
INTO TEMPORARY TABLE probes2
from PRB_Probe pp, PRB_Reference pr
where pp._Probe_key = pr._Probe_key
group by pp._Probe_key, pr._Refs_key having count(*) > 1
;

create index idx1_probes on probes(_Probe_key)
;
create index idx1_probes2 on probes2(_Probe_key)
;
create index idx2_probes2 on probes2(_Refs_key)
;


\echo ''
\echo 'Probes/Primers w/out References'
\echo ''

select p.name, m.symbol, p._Probe_key 
from probes p, PRB_Marker pm, MRK_Marker m
where p._Probe_key = pm._Probe_key
and pm._Marker_key = m._Marker_key
order by p.name, m.symbol
;

\echo ''
\echo 'Probes/Primers with duplicate References'
\echo ''

select pp.name, r.jnumID
from probes2 p, PRB_Probe pp, BIB_Citation_Cache r
where p._Probe_key = pp._Probe_key
and p._Refs_key = r._Refs_key
order by pp.name
;

\echo ''
\echo 'Probes/Amplification Primers with No Markers in Common'
\echo ''

select pa.accid as mgiid_of_probe, p.name as name_of_probe, pamp.accid as mgdiid_of_primer, amp.name as name_of_primer,
m1.symbol as symbol_of_probe, m2.symbol as symbol_of_primer
from prb_probe p, acc_accession pa, prb_marker pm, mrk_marker m1,
prb_probe amp, acc_accession pamp, prb_marker mamp, mrk_marker m2
where p.ampprimer is not null
and not exists (select 1 from prb_marker pm, mrk_marker m1, prb_probe amp, prb_marker mamp, mrk_marker m2
        where p._probe_key = pm._probe_key
        and pm._marker_key = m1._marker_key
        and p.ampPrimer = amp._probe_key
        and amp._probe_key = mamp._probe_key
        and mamp._marker_key = m2._marker_key
        and m1.symbol = m2.symbol
        )
and p._probe_key = pm._probe_key
and p._probe_key = pa._object_key
and pa._mgitype_key = 3
and pa._logicaldb_key = 1
and pm._marker_key = m1._marker_key
and p.ampPrimer = amp._probe_key
and amp._probe_key = pamp._object_key
and pamp._mgitype_key = 3
and pamp._logicaldb_key = 1
and amp._probe_key = mamp._probe_key
and mamp._marker_key = m2._marker_key
and m1.symbol != m2.symbol
order by mgiid_of_probe desc
;

select distinct c._Probe_key, s._Sequence_key, c._CreatedBy_key, c.annotation_date
INTO TEMPORARY TABLE probedummy
from SEQ_Probe_Cache c, SEQ_Sequence s
where c._Sequence_key = s._Sequence_key
and s._SequenceStatus_key = 316345
;

create index probedummy_idx1 on probedummy(_Probe_key)
;
create index probedummy_idx2 on probedummy(_Sequence_key)
;
create index probedummy_idx3 on probedummy(_CreatedBy_key)
;

select p.*
INTO TEMPORARY TABLE probedummy2
from probedummy p, PRB_Probe pp, PRB_Source s
where p._Probe_key = pp._Probe_key
and pp._Source_key = s._Source_key
and s._Organism_key = 1
;

create index probedummy2_idx1 on probedummy2(_Probe_key)
;
create index probedummy2_idx2 on probedummy2(_Sequence_key)
;
create index probedummy2_idx3 on probedummy2(_CreatedBy_key)
;

\echo ''
\echo 'Dummy Sequence Records Annotated to GXD Mouse Molecular Segments'
\echo ''

select distinct ma.accID as "MGI ID", 
       p.name as "Molecular Segment", 
       sa.accID as "Sequence", 
       l.name,
       u.login, 
       d.annotation_date
from probedummy2 d, PRB_Probe p, GXD_ProbePrep g, ACC_Accession ma, ACC_Accession sa, ACC_LogicalDB l, MGI_User u
where d._Probe_key = p._Probe_key
and d._Probe_key = g._Probe_key
and d._Probe_key = ma._Object_key
and ma._MGIType_key = 3
and ma._LogicalDB_key = 1
and ma.prefixPart = 'MGI:'
and ma.preferred = 1
and d._Sequence_key = sa._Object_key
and sa._MGIType_key = 19
and sa.preferred = 1
and sa._LogicalDB_key = l._LogicalDB_key
and d._CreatedBy_key = u._User_key
order by l.name, d.annotation_date, p.name
;

select s._Sequence_key
INTO TEMPORARY TABLE deleted1
from SEQ_Sequence s
where s._SequenceStatus_key = 316343
;

create index deleted1_idx1 on deleted1(_Sequence_key)
;

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

select d.accID as seqID, pa2.accID as mgiID, substring(p.name,1,30) as name
INTO TEMPORARY TABLE pdeleted
from deleted2 d, SEQ_Probe_Cache pa, ACC_Accession pa2, PRB_Probe p, GXD_ProbePrep g
where d._Sequence_key = pa._Sequence_key
and pa._Probe_key = pa2._Object_key
and pa2._MGIType_key = 3
and pa2._LogicalDB_key = 1
and pa2.prefixPart = 'MGI:'
and pa2.preferred = 1
and pa._Probe_key = p._Probe_key
and pa._Probe_key = g._Probe_key
;

create index pdeleted_idx1 on pdeleted(seqID)
;

\echo ''
\echo 'Deleted Sequences with GXD Associations'
\echo ''
\echo 'A row in this report represents a Sequence that is designated as Deleted'
\echo 'by the Sequence provider and contains associations to a GXD Molecular Segment.'
\echo ''

select seqID, mgiID, name from pdeleted
;

select distinct pm._Probe_key, pm._Marker_key
INTO TEMPORARY TABLE encodes
from PRB_Marker pm, GXD_ProbePrep g
where g._Probe_key = pm._Probe_key
and pm.relationship = 'E'
;

select _Probe_key INTO TEMPORARY TABLE multencodes from encodes group by _Probe_key having count(*) > 1
;
create index multencodes_idx1 on multencodes(_Probe_key)
;

\echo ''
\echo 'Probe w/ more than one encodes relationship'
\echo ''

select distinct a.accid, p.name, m.symbol
from multencodes e, encodes ee, PRB_Probe p, MRK_Marker m, ACC_Accession a
where e._Probe_key = p._Probe_key
and e._Probe_key = a._Object_key
and a._MGIType_key = 3
and a._Logicaldb_key = 1
and a.prefixPart = 'MGI:'
and a.preferred = 1
and e._Probe_key = ee._Probe_key
and ee._Marker_key = m._Marker_key
order by a.accid
;

\echo ''
\echo 'Antibodies with source information but both tissue and cell line are Not specified'
\echo ''

select distinct _Antibody_key, antibodyName, mgiID 
INTO TEMPORARY TABLE antibodies
from GXD_Antibody_View g, PRB_Source s 
where s._Source_key = g._Source_key 
and g.antigenOrganismKey = 1  
and g._CellLine_key = 316335  
and g._Tissue_key = -1  
and s.description is not null
;

INSERT INTO antibodies
select distinct _Antibody_key, antibodyName, mgiID 
from GXD_Antibody_View 
where antigenOrganismKey = 1
and _CellLine_key = 316335 
and _Tissue_key = -1 
and (age != 'Not Specified' 
or _Strain_key != -1 
or _Gender_key != 315167)
;

select mgiID, antibodyName
from antibodies
;

\echo ''
\echo 'Mouse cDNAs with gene associations and source information but both tissue and cell line are Not specified'
\echo ''

select distinct m._Probe_key, m.name as cDNAname, p.mgiID 
INTO TEMPORARY TABLE probes3
from PRB_Source s, PRB_Probe_View p, PRB_Marker_View m
where s._Organism_key = 1 
and p._SegmentType_key = 63468 
and s._CellLine_key = 316335 
and s._Tissue_key = -1 
and s._Source_key = p._Source_key 
and p._Probe_key = m._Probe_key 
and (s.age != 'Not Specified' 
or s._Strain_key != -1 
or s._Gender_key != 315167)
;

INSERT INTO probes3
select distinct m._Probe_key, m.name, p.mgiID 
from PRB_Source s, PRB_Probe_View p, PRB_Marker_View m
where s._Organism_key = 1 
and p._SegmentType_key = 63468 
and s._CellLine_key = 316335 
and s._Tissue_key = -1 
and s._Source_key = p._Source_key 
and p._Probe_key = m._Probe_key 
and s.description is not null
;

select mgiID, cDNAname from probes3
;

\echo ''
\echo 'Duplicate RNAscope Probes (Mm-%)'
\echo ''
select name 
INTO TEMPORARY TABLE probes4
from PRB_Probe 
where name like 'Mm-%' 
group by name having count(*) > 1
;

create index idx4_probes on probes4(name)
;

select p.name, p.mgiID
from probes4, PRB_Probe_View p
where probes4.name = p.name
;

\echo ''
\echo 'Duplicate Taqman Primer (Mm%)'
\echo ''
select p.name 
INTO TEMPORARY TABLE probes5
from PRB_Probe p
where (p.name like 'Mm%' and p.name not like 'Mmp%')
and p._segmenttype_key = 63473
group by name having count(*) > 1
union
select p.name 
from PRB_Probe p, MGI_Note n
where p.name like 'Mm%' 
and p._segmenttype_key = 63473
and p._probe_key = n._object_key
and n._mgitype_key = 3
and n.note like '%taqman%'
group by name having count(*) > 1
union
select p.name 
from PRB_Probe p, MGI_Note n
where p._probe_key = n._object_key
and n._mgitype_key = 3
and n.note like '%taqman%'
group by name having count(*) > 1
;

create index idx5_probes on probes5(name)
;

select p.name, p.mgiID
from probes5, PRB_Probe_View p
where probes5.name = p.name
;

\echo ''
\echo 'Primers whose sequence field contains a hyphen'
\echo ''
select p.name, a.accid
from PRB_Probe p, ACC_Accession a
where p._probe_key = a._object_key
and a._mgitype_key = 3
and (p.primer1sequence like '%-%' or p.primer2sequence like '%-%')
order by p.name
;
