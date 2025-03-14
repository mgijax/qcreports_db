select a._Assay_key, a._Marker_key, p._Probe_key, u.login
INTO TEMPORARY TABLE probe
from GXD_Assay a, GXD_ProbePrep p, MGI_User u
where a._ProbePrep_key = p._ProbePrep_key
and a._AssayType_key in (1,2,3,4,5,6,8)
and a._Modifiedby_key = u._User_key
;

\echo ''
\echo 'GXD Assay Probe/Marker Pairs No Longer Found in Master Probe Table'
\echo ''

select a.accID as "Assay", pb.name as "Probe", m.symbol as "Marker", p.login
from probe p, PRB_Probe pb, MRK_Marker m, ACC_Accession a
where p._Probe_key = pb._Probe_key
and p._Marker_key = m._Marker_key
and p._Assay_key = a._Object_key
and a._MGIType_key = 8
and not exists (select 1 from PRB_Marker pm
                where p._Probe_key = pm._Probe_key
                and p._Marker_key = pm._Marker_key)
;

select a._Assay_key, a._Marker_key, p._Antibody_key, u.login
INTO TEMPORARY TABLE antibody
from GXD_Assay a, GXD_AntibodyPrep p, MGI_User u
where a._AntibodyPrep_key = p._AntibodyPrep_key
and a._AssayType_key in (1,2,3,4,5,6,8)
and a._Modifiedby_key = u._User_key
;

\echo ''
\echo 'GXD Assay Antibody/Marker Pairs No Longer Found in Master Antibody Table'
\echo ''

select m.symbol as "Marker", substring(b.antibodyName,1,75) as "Antibody", a.accID as "Assay", p.login
from antibody p, GXD_Antibody b, MRK_Marker m, ACC_Accession a
where p._Antibody_key = b._Antibody_key
and p._Marker_key = m._Marker_key
and p._Assay_key = a._Object_key
and a._MGIType_key = 8
and not exists (select 1 from GXD_AntibodyMarker bm
                where p._Antibody_key = bm._Antibody_key
                and p._Marker_key = bm._Marker_key)
;

select a._Assay_key, a._Refs_key, p._Probe_key, u.login
INTO TEMPORARY TABLE proberef
from GXD_Assay a, GXD_ProbePrep p, MGI_User u
where a._ProbePrep_key = p._ProbePrep_key
and a._AssayType_key in (1,2,3,4,5,6,8)
and a._Modifiedby_key = u._User_key
and not exists (select 1 from PRB_Reference r
		where p._Probe_key = r._Probe_key
                and a._Refs_key = r._Refs_key)
;

\echo ''
\echo 'GXD Assay Probes with no corresponding entry in the Probe Reference Table'
\echo ''

select a.accID as "Assay", b.accID as "J Number", pb.name as "Probe", p.login
from proberef p, ACC_Accession a, ACC_Accession b, PRB_Probe pb
where p._Assay_key = a._Object_key
and a._MGIType_key = 8
and p._Refs_key = b._Object_key
and b._MGIType_key = 1
and b._LogicalDB_key = 1 
and b.prefixPart = 'J:'
and p._Probe_key = pb._Probe_key
order by pb.name, a.accID
;

