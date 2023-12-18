
'''
   pm2gene Refs not in MGI

    * Mouse
    * PubMedID not in MGI
    * <= 15 egIDs/PubMedID
    * ALL egIDs in MGI
    * ALL egIDs for markers with feature type "protein coding gene" or "miRNA gene"
    * ALL egIDs associated with a single marker
    * ALL egIDs (markers represented by) NOT used in a GO annotation, unless 
       evidence code is (ISO, IBA or IEA), i.e. if the GO annotation has one of 
       these evidence codes, it's not a condition to exclude the marker.

'''

import sys 
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

# pmID:[egID, ...], ...}
inputPmToEgDict = {}

# lookup of egIDs for marker with GO annotations excluding ISO, IBA, IEA
# evidence codes
mrkGOAnnotList = []

# list of markers with feature type protein coding gene or miRNA gene
goReportMarkers = []

# {egID:[ [m1,symbols1, markerKey] ...], ...}
dbEgToMarkerDict = {}

fp = reportlib.init(sys.argv[0], '', os.environ['QCOUTPUTDIR'])

fp.write('PM2Gene References not in MGI\n\n')
fp.write('    * Mouse\n')
fp.write('    * PubMedID not in MGI\n')
fp.write('    * <= 15 egIDs/PubMedID\n')
fp.write('    * ALL egIDs in MGI\n')
fp.write('    * ALL egIDs for markers with feature type "protein coding gene" or "miRNA gene"\n')
fp.write('    * ALL egIDs associated with a single marker\n')
fp.write('''    * ALL egIDs (markers represented by) NOT used in a GO annotation, unless 
       evidence code is (ISO, IBA or IEA), i.e. if the GO annotation has one of 
       these evidence codes, it's not a condition to exclude the marker.\n\n''')
fp.write('PM ID%sEG IDs%s%s' % (TAB, TAB, CRT))

# -- use to determine if egID assoc >1 marker
# -- report EG ID and gene mgiID and marker symbol
results = db.sql('''
    select a1.accid as egID, m._Marker_key, m.symbol, a2.accid as markerID
    from ACC_Accession a1, MRK_Marker m, ACC_Accession a2
    where a1._MGIType_key = 2
    and a1._LogicalDB_key = 55
    and a1.preferred = 1
    and a1._Object_key = m._Marker_key
    and a1._Object_key = a2._Object_key
    and a2._MGIType_key = 2
    and a2._LogicalDB_key = 1
    and a2.preferred = 1
    and a2.prefixPart = 'MGI:'
    order by a1.accid
    ''', 'auto')
for r in results:
    egID = r['egID']
    markerID = r['markerID']
    symbol = r['symbol']
    markerKey = r['_Marker_key']
    if egID not in dbEgToMarkerDict:
        dbEgToMarkerDict[egID] = []
    listToAppend = [markerID, symbol, markerKey]
    if listToAppend not in dbEgToMarkerDict[egID]:
        dbEgToMarkerDict[egID].append(listToAppend)

results = db.sql('''
    select a.accid as egID
    from mrk_mcv_cache m, acc_accession a
    where m.term in ('protein coding gene', 'miRNA gene')
    and m.qualifier = 'D'
    and m._marker_key = a._object_key
    and a._mgitype_key = 2
    and a.preferred = 1
    and a._logicaldb_key = 55
    ''', 'auto')
for r in results:
    goReportMarkers.append(r['egID'])

results = db.sql('''
    select distinct aa.accid as egID
    from VOC_Annot va, VOC_Evidence e, ACC_Accession aa
    where va._AnnotType_key = 1000
    and va._term_key not in (1098, 6113, 120)
    and va._object_key = aa._Object_key
    and aa._mgitype_key= 2
    and aa._logicaldb_key = 55 --entrezgene
    and va._annot_key = e._annot_key
    and e._evidenceterm_key not in (115, 3251466, 7428292)
    ''', 'auto')
    # IEA, ISO, IBA

for r in results:
    mrkGOAnnotList.append(r['egID'])

db.sql('''
    select a1._Object_key as refsKey, a1.accid as mgiID, a3.accid as pubmedid
    into temporary table pmInMGIwithJnum
    from ACC_Accession a1, ACC_Accession a2, ACC_Accession a3
    where a1._MGIType_key = 1
    and a1._LogicalDB_key = 1
    and a1.preferred = 1
    and a1.prefixPart = 'MGI:'
    and a1._Object_key = a2._Object_key
    and a2._MGIType_key = 1
    and a2._LogicalDB_key = 1
    and a2.prefixPart = 'J:'
    and a2.preferred = 1
    and a1._Object_key = a3._Object_key
    and a3._MGIType_key = 1
    and a3._LogicalDB_key = 29
    and a3.preferred = 1
    ''', None) # 28,4770

# EG Mouse PubMed IDs 
db.sql('''create index idx1 on pmInMGIwithJnum(pubmedid)''', None)
db.sql('''
    select geneid, pubmedid
    into temporary table egPMIDs
    from DP_EntrezGene_PubMed
    where taxid = 10090
    ''', None) # 1,202,493
db.sql('''create index idx2 on egPMIDs(pubmedid)''', None)

# EG Mouse PubMed IDs not in MGI
results = db.sql('''
    select eg.*
    from egPMIDs eg
    where not exists (select 1
    from pmInMGIwithJnum inMGI
    where eg.pubmedid = inMGI.pubmedid)
    ''', 'auto') # 203,864

for r in results:
    pmID = r['pubmedid']
    egID = r['geneid']
    if pmID  not in inputPmToEgDict:
        inputPmToEgDict[pmID] = []
    inputPmToEgDict[pmID].append(egID)

pmIdCt = 0
for pmID in inputPmToEgDict:

    egList = inputPmToEgDict[pmID]

    skipPmID = 0

    # skip this pmID if it has > 15 egIDs
    if len(egList) > 15: # 142
        #continue
        skipPmID = 1

    for egID in egList:

        # egID must be protein coding or miRNA feature type, if one isn't skip this pmID
        if egID not in goReportMarkers: # 99391 /99533
            skipPmID = 1

        #  if any egID not in the the database, skip
        if egID not in dbEgToMarkerDict: # 99533
            skipPmID = 1

        # if any egID assoc > 1 marker skip
        if egID in dbEgToMarkerDict and len(dbEgToMarkerDict[egID]) > 1: # 0
            skipPmID = 1

        # if any egID has GO annotations (see excluded evidenc above, skip
        if egID in mrkGOAnnotList: # 0
            skipPmID = 1

        if skipPmID == 1:
            break # skip this pmID

    if skipPmID == 0:
        # Otherwise write the pmID and its set of egIDs to the report
        fp.write('%s%s%s%s' % (pmID, TAB, ', '.join(egList), CRT))    
        pmIdCt += 1

fp.write('Total: %s' % pmIdCt)
reportlib.finish_nonps(fp)
