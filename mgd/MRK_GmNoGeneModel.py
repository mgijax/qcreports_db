'''
#
# MRK_GmNoGeneModel.py
#
# Report:
#
# 1. MGI_ID
# 2. Symbol
# 3. Old Symbol
# 4. Chromomse
# 5. FeatureType
# 6. NomenJnum: the original J# used for creating the marker
# 7. GenBank_RefSeq: comma seperated IDs
# 8. Obsolete Genbank_RefSeq
# 9. UniProt: comma seperated IDs
# 10. EntrezID/NCBI_ID
# 11. goCount: exclude annotations for "No experimental evidence"
# 12. expressionCount: just classical expression data
# 13. orthoCount
# 14. alleleCount
# 15. allNucleicCount
# 16. microarray_probesets
# 17. primerCount
#
# History:
#
# lec   05/06/2025
#   wts2-1655/e4g-252/Enhance QC report MRK_GmNoGeneModel.sql.rpt
#   moved *sql -> *py version
#
'''
 
import sys 
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = ' | '

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

fp.write("Gm Markers without Gene Model Associations" + CRT)
fp.write("   where name begins ''predicted gene'''" + CRT)
fp.write("   and status = ''official''" + CRT*2)

fp.write('MGI_ID' + TAB)
fp.write('Symbol' + TAB)
fp.write('Old Symbol' + TAB)
fp.write('Chromomse' + TAB)
fp.write('FeatureType' + TAB)
fp.write('NomenJnum' + TAB)
fp.write('GenBank_RefSeq' + TAB)
fp.write('Obsolete Genbank_RefSeq' + TAB)
fp.write('UniProt' + TAB)
fp.write('EntrezID/NCBI_ID' + TAB)
fp.write('goCount' + TAB)
fp.write('expressionCount' + TAB)
fp.write('orthoCount' + TAB)
fp.write('alleleCount' + TAB)
fp.write('allNucleicCount' + TAB)
fp.write('microarray_probesets' + TAB)
fp.write('primerCount' + CRT*2)

db.sql('''
select distinct m._marker_key, a.accID, m.symbol, m.name, m.chromosome, t.term as featureType, c.jnumid
into temp table markers
from MRK_Marker m, ACC_Accession a, VOC_Annot v, VOC_Term t, MRK_History h, BIB_Citation_Cache c
where m._organism_key = 1
and m._marker_Status_key = 1
and m.name like 'predicted gene%'
and m._marker_key = v._object_key
and v._annotType_key = 1011
and v._term_key = t._term_key
and m._marker_key = h._marker_key
and h.sequenceNum = 1
and h._refs_key = c._refs_key
and not exists (select 1 from SEQ_marker_Cache c
where m._marker_key = c._marker_key
and c._logicaldb_key in (59,60))
and m._marker_key = a._object_key
and a._mGitype_key = 2
and a._logicaldb_Key = 1
and a.prefixPart = 'MGI:'
and a.preferred = 1
''', None)

db.sql(''' create index idx_marker on markers(_marker_key); ''', None)

db.sql('''
select m._marker_key, hm.symbol as oldSymbol, substring(h.name,1,50) as oldName
into temp table history
from markers m, MRK_History h, MRK_Marker hm
where m._marker_key = h._marker_key
and m.name != h.name
and h._History_key = hm._marker_key
and m.symbol != hm.symbol
''', None)

db.sql(''' create index idx_history on history(_marker_key); ''', None)

# 7. GenBank_RefSeq: comma seperated IDs
# 9. UniProt: comma seperated IDs
# 10. EntrezID/NCBI_ID
genbankIds = {}
entrezIds = {}
uniprotIds = {}
results = db.sql('''
select m._marker_key, a.accid, a._logicaldb_key
from markers m, acc_accession a
where m._marker_key = a._object_key
and a._mgitype_key = 2
and a._logicaldb_key in (9, 27, 55, 13, 41)
''', 'auto')
for r in results:
    key = r['_marker_key']
    ldbkey = r['_logicaldb_key']
    accid = r['accid']

    if ldbkey in (9,27):
        if key not in genbankIds:
            genbankIds[key] = []
        genbankIds[key].append(accid)
    elif ldbkey == 55:
        if key not in entrezIds:
            entrezIds[key] = []
        entrezIds[key].append(accid)
    elif ldbkey in (13, 41):
        if key not in uniprotIds:
            uniprotIds[key] = []
        uniprotIds[key].append(accid)
#print(genbankIds)
#print(entrezIds)
#print(uniprotIds)

# 8. Obsolete Genbank_RefSeq
obsoleteGenbankIds = {}
results = db.sql('''
select m._marker_key, a.accid
from markers m, acc_accession a, acc_accession s, seq_sequence ss
where m._marker_key = a._object_key
and a._mgitype_key = 2
and a._logicaldb_key in (9, 27)
and a.accid = s.accid
and s._mgitype_key = 19
and s._logicaldb_key in (9, 27)
and s._object_key = ss._sequence_key
and ss._SequenceStatus_key = 316343
''', 'auto')
for r in results:
    key = r['_marker_key']
    accid = r['accid']
    if key not in obsoleteGenbankIds:
        obsoleteGenbankIds[key] = []
    obsoleteGenbankIds[key].append(accid)

# 11. goCount: exclude annotations for "No experimental evidence"
goCount = {}
results = db.sql('''
select m._marker_key, count(distinct va._Term_key) as pcount
from markers m, VOC_Annot va, VOC_Evidence ev
where m._marker_key = va._Object_key
and va._AnnotType_key = 1000
and va._Annot_key = ev._Annot_key
and ev._EvidenceTerm_key not in (115, 118, 114, 3251496)
group by m._marker_key
''', 'auto')
for r in results:
    key = r['_marker_key']
    if key not in goCount:
        goCount[key] = []
    goCount[key].append(r['pcount'])

# 12. expressionCount: just classical expression data
expressionCount = {}
results = db.sql('''
select m._marker_key, count(distinct e._assay_key) as pcount
from markers m, gxd_expression e
where m._marker_key = e._marker_key
group by m._marker_key
''', 'auto')
for r in results:
    key = r['_marker_key']
    if key not in expressionCount:
        expressionCount[key] = []
    expressionCount[key].append(r['pcount'])

# 13. orthoCount
orthoCount = {}
results = db.sql('''
select m1._marker_key, count(distinct m2._Marker_key) as pcount
from markers m1, MRK_Marker m2,
MRK_Cluster mc,
MRK_ClusterMember h1,
MRK_ClusterMember h2
where m1._marker_key = h1._marker_key
and mc._ClusterSource_key = 75885739
and mc._Cluster_key = h1._Cluster_key
and h1._Cluster_key = h2._Cluster_key
and h2._Marker_key = m2._Marker_key
and m2._Organism_key != 1
group by m1._marker_key
''', 'auto')
for r in results:
    key = r['_marker_key']
    if key not in orthoCount:
        orthoCount[key] = []
    orthoCount[key].append(r['pcount'])

# 14. alleleCount
alleleCount = {}
results = db.sql('''
select m._marker_key, count(a._allele_key) as pcount
from markers m, all_allele a
where m._marker_key = a._marker_key
and a.iswildtype = 0
group by m._marker_key
''', 'auto')
for r in results:
    key = r['_marker_key']
    if key not in alleleCount:
        alleleCount[key] = []
    alleleCount[key].append(r['pcount'])

# 15. allNucleicCount
allNucleicCount = {}
results = db.sql('''
select m._marker_key, count(p._probe_key) as pcount
from markers m, prb_marker p, prb_probe pp
where m._marker_key = p._marker_key
and p._probe_key = pp._probe_key
and pp._segmenttype_key != 63473
group by m._marker_key
''', 'auto')
for r in results:
    key = r['_marker_key']
    if key not in allNucleicCount:
        allNucleicCount[key] = []
    allNucleicCount[key].append(r['pcount'])
#print(allNucleicCount)

# 16. microarray_probesets
microarrayCount = {}
results = db.sql('''
select m.symbol, m._marker_key, count(a._accession_key) as pcount
from markers m, acc_accession a
where m._marker_key = a._object_key
and a._logicaldb_key = 122
group by m.symbol, m._marker_key
''', 'auto')
for r in results:
    key = r['_marker_key']
    if key not in microarrayCount:
        microarrayCount[key] = []
    microarrayCount[key].append(r['pcount'])
#print(microarrayCount)

# 17. primerCount
primerCount = {}
results = db.sql('''
select m._marker_key, count(p._probe_key) as pcount
from markers m, prb_marker p, prb_probe pp
where m._marker_key = p._marker_key
and p._probe_key = pp._probe_key
and pp._segmenttype_key = 63473
group by m._marker_key
''', 'auto')
for r in results:
    key = r['_marker_key']
    if key not in primerCount:
        primerCount[key] = []
    primerCount[key].append(r['pcount'])
#print(primerCount)

# final report

results = db.sql('''
select m.*, h.oldSymbol, h.oldName
from markers m, history h
where m._marker_key = h._marker_key
union
select m.*, null, null
from markers m
where not exists (select 1 from history h where m._marker_key = h._marker_key)
order by symbol
''', 'auto')

for r in results:
    key = r['_marker_key']

    # 1. MGI_ID
    fp.write(r['accID'] + TAB)

    # 2. Symbol
    fp.write(r['symbol'] + TAB)

    # 3. Old Symbol
    if r['oldSymbol'] != None:
        fp.write(r['oldSymbol'])
    fp.write(TAB)

    # 4. Chromomse
    fp.write(r['chromosome'] + TAB)

    # 5. FeatureType
    fp.write(r['featureType'] + TAB)

    # 6. NomenJnum: the original J# used for creating the marker
    fp.write(r['jnumid'] + TAB)

    # 7. GeneBank: comma seperated IDs
    if key in genbankIds and key not in obsoleteGenbankIds:
        fp.write(','.join(genbankIds[key]))
    fp.write(TAB)

    # 8. Obsolete Genbank_RefSeq
    if key in obsoleteGenbankIds:
        fp.write(','.join(obsoleteGenbankIds[key]))
    fp.write(TAB)

    # 9. UniProt: comma seperated IDs
    if key in uniprotIds:
        fp.write(','.join(uniprotIds[key]))
    fp.write(TAB)

    # 10. EntrezID/NCBI_ID
    if key in entrezIds:
        fp.write(','.join(entrezIds[key]))
    fp.write(TAB)

    # 11. goCount: exclude annotations for "No experimental evidence"
    if key in goCount:
        fp.write(str(goCount[key][0]) + TAB)
    else:
        fp.write('0' + TAB)

    # 12. expressionCount: just classical expression data
    if key in expressionCount:
        fp.write(str(expressionCount[key][0]) + TAB)
    else:
        fp.write('0' + TAB)

    # 13. orthoCount
    if key in orthoCount:
        fp.write(str(orthoCount[key][0]) + TAB)
    else:
        fp.write('0' + TAB)

    # 14. alleleCount
    if key in alleleCount:
        fp.write(str(alleleCount[key][0]) + TAB)
    else:
        fp.write('0' + TAB)

    # 15. allNucleicCount
    if key in allNucleicCount:
        fp.write(str(allNucleicCount[key][0]) + TAB)
    else:
        fp.write('0' + TAB)

    # 16. microarray_probesets
    if key in microarrayCount:
        fp.write(str(microarrayCount[key][0]) + TAB)
    else:
        fp.write('0' + TAB)

    # 17. primerCount
    if key in primerCount:
        fp.write(str(primerCount[key][0]) + CRT)
    else:
        fp.write('0' + CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)
