'''
   Papers in public MGI for genes with no MP annotations

    * Mouse
    * Has a J number assignment in MGI (paper may be in keep or discard status)
    * Has a lit triage status of “not routed”, "routed" or "Chosen" for AP
    * Does NOT have a lit triage tag of "AP:New_allele_new_gene"
    * Have <= 15 egIDs per PubMed ID
    * Publication Year > 1999
    * For eg ids that are mapped to an MGI marker, 
      include publications that have any egID whose MGI marker does not have rolled up MP annotations 
      (excluding MP annotations that are made using J:211773, J:165965, J:171883, J:175295, J:175213, J:239583, J:100221)
'''

import sys 
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

# pmID:[egID, ...], ...}
pmEG = {}

# pmID: info
pmInfo = {}

# egID marker meets genotype criteria
pmGenotype = []

fp = reportlib.init(sys.argv[0], '', os.environ['QCOUTPUTDIR'])

fp.write('Papers in public MGI for genes with no MP annotations\n\n')
fp.write('    * Mouse\n')
fp.write('    * Have <= 15 egIDs per PubMed ID\n')
fp.write('    * Has a J number assignment in MGI (paper may be in keep or discard status)\n')
fp.write('    * Has a lit triage status of “not routed”, "routed" or "Chosen" for AP\n')
fp.write('    * Does NOT have a lit triage tag of AP:New_Allele_new_gene\n')
fp.write('    * Publication Year > 1999\n')
fp.write('    * For eg ids that are mapped to an MGI marker,\n')
fp.write('      include publications that have any egID whose MGI marker does not have rolled up MP annotations\n')
fp.write('      (excluding MP annotations that are made using J:211773, J:165965, J:171883, J:175295, J:175213, J:239583, J:100221\n\n')
fp.write('PM ID%sRelevance%sEG IDs%s' % (TAB, TAB, CRT))

# EG Mouse PubMed IDs in MGI/J# is not null
# EG Mouse PubMed IDs not in MGI
db.sql('''
    select eg.geneid, eg.pubmedid, c.relevanceTerm
    into temporary table egPMIDs
    from DP_EntrezGene_PubMed eg, BIB_Citation_Cache c, BIB_Refs r
    where eg.taxid = 10090
    and eg.pubmedid = c.pubmedid
    and c.jnumID is not null
    and c._refs_key = r._refs_key
    and r.year > 1999
    and exists (select 1 from BIB_Workflow_Status s
        where c._refs_key = s._refs_key
        and s.isCurrent = 1
        and s._group_key = 31576664
        and s._status_key in (31576669,31576671,31576671)
        )
    and not exists (select 1 from BIB_Workflow_Tag s
        where c._refs_key = s._refs_key
        and s._tag_key = 35710200
        )
    ''', None) 
db.sql('''create index idx1 on egPMIDs(pubmedid)''', None)
db.sql('''create index idx2 on egPMIDs(geneid)''', None)

# EG Mouse PubMed in or not in MGI
results = db.sql('''select * from egPMIDs order by geneid, relevanceTerm''', 'auto')
for r in results:
    pmID = r['pubmedid']
    egID = r['geneid']
    if pmID not in pmEG:
        pmEG[pmID] = []
    pmEG[pmID].append(egID)
    if pmID not in pmInfo:
        pmInfo[pmID] = []
    pmInfo[pmID].append(r['relevanceTerm'])
        
#
# EG Mouse PubMed IDs that have Genotypes
#       genotype does not have MP annot that is not:
#               J:211773, J:165965, J:171883, J:175295, J:175213, J:239583, J:100221
#
results = db.sql('''
        -- genotypes do not have any MP annotations
        select eg.pubmedid
        from egPMIDs eg
        where not exists (select 1 from acc_accession a, gxd_allelegenotype g, voc_annot va, voc_evidence e, bib_citation_cache c
                where eg.geneid = a.accid
                and a._logicaldb_key = 55
                and a._mgitype_key = 2
                and a._object_key = g._marker_key
                and g._genotype_key = va._object_key and va._annottype_key = 1002
                and va._annot_key = e._annot_key
                and e._refs_key = c._refs_key
                )
        union
        -- genotypes have MP annotations but only to given J:'s
        select eg.pubmedid
        from egPMIDs eg
        where exists (select 1 from acc_accession a, gxd_allelegenotype g, voc_annot va, voc_evidence e, bib_citation_cache c
                where eg.geneid = a.accid
                and a._logicaldb_key = 55
                and a._mgitype_key = 2
                and a._object_key = g._marker_key
                and g._genotype_key = va._object_key and va._annottype_key = 1002
                and va._annot_key = e._annot_key
                and e._refs_key = c._refs_key
                and c.jnumid in ('J:211773','J:165965','J:171883','J:175295','J:175213','J:239583','J:100221')
                )
        and not exists (select 1 from acc_accession a, gxd_allelegenotype g, voc_annot va, voc_evidence e, bib_citation_cache c
                where eg.geneid = a.accid
                and a._logicaldb_key = 55
                and a._mgitype_key = 2
                and a._object_key = g._marker_key
                and g._genotype_key = va._object_key and va._annottype_key = 1002
                and va._annot_key = e._annot_key
                and e._refs_key = c._refs_key
                and c.jnumid not in ('J:211773','J:165965','J:171883','J:175295','J:175213','J:239583','J:100221')
                )
    ''', 'auto')
for r in results:
    pmID = r['pubmedid']
    if pmID not in pmGenotype:
        pmGenotype.append(pmID)

counter = 0
for pmID in pmEG:

    # skip > 15 egIDs
    egList = pmEG[pmID]
    if len(egList) > 15:
        continue

    # skip if not passes genotype rules
    if pmID not in pmGenotype:
        continue

    counter += 1
    relevanceTerm = pmInfo[pmID][0]
    if relevanceTerm == None:
        relevanceTerm = ""

    fp.write('%s%s%s%s%s%s' % (pmID, TAB, relevanceTerm, TAB, ', '.join(egList), CRT))

fp.write('\nTotal: %s\n' % counter)
reportlib.finish_nonps(fp)

