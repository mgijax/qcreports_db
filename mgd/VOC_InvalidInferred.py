'''
#
# VOC_InvalidInferred.py 10/17/2003
#
# Report:
#	TR 5311
#
#       Tab-delimited file
#       Annotation Evidence Inferred From Accession IDs
#	which are invalid.
#
# Usage:
#       VOC_InvalidInferred.py
#
# Used by:
#       Annotation Editors
#
# Notes:
#
# History:
#
# lec   11/03/2023
#       wts2-1321/fl2-616/add PMID to Invalid Inferred From Values report
#       commented out "print" statements; turn on for debugging only
#
# sc    03/30/2021
#       - TR13485/removed the final query of the database because it was
#       picking more ids than it should. See TR for more info:
#       for t in theDiffs:
#       infoList = inferredLookup[t]
#       for s in infoList:
#               fp.write(t + reportlib.TAB + s)
#               rows = rows + 1
#       This was being plugged into a query using the realid - 
#       but it was returning more than it should because of the wildcard suffix:
#       toSelect = '%' + t + '%'
#       
# lec	07/25/2016
#	- TR12222/expects only one delimiter, but *any* delimiter may be used in inferredFrom field
#
# lec	11/18/2014
#	- TR11828/remove "," from report; this is an allowed value
#
# lec	12/28/2011
#	- TR10934/replace any commas in WITH field with pipe
#
# lec	04/05/2011
#	- TR10650/add GO/add Set
#
# lec	11/14/2003
#	- new
#
'''
 
import sys
import os
import Set
import mgi_utils
import reportlib
import db

db.setTrace()

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])
fp.write('\nInvalid "Inferred From" Values in GO Annotations (MGI, GO, PMID, ";")' + 2 * reportlib.CRT)
fp.write('field 1 : Inferred From Value that is invalid' + reportlib.CRT)
fp.write('field 2 : GO ID' + reportlib.CRT)
fp.write('field 3 : Evidence Code' + reportlib.CRT)
fp.write('field 4 : Marker Symbol' + reportlib.CRT)
fp.write('field 5 : PubMedID of GO/Reference' + 2* reportlib.CRT)

rows = 0

# read in all MGI accession ids for Markers (2), Alleles (11)
# read in all GO ids (13)
# read in all PMID ids (29)
# this is the list of valid accession ids

mgiLookup = []
results = db.sql('select a.accID from ACC_Accession a where a._MGIType_key in (2, 11) and a.prefixPart = \'MGI:\'', 'auto')
for r in results:
    mgiLookup.append(r['accID'])
results = db.sql('select a.accID from ACC_Accession a where a._MGIType_key = 13 and a.prefixPart in (\'GO:\')', 'auto')
for r in results:
    mgiLookup.append(r['accID'])
results = db.sql('select a.accID from ACC_Accession a where a._MGIType_key = 29', 'auto')
for r in results:
    mgiLookup.append(r['accID'])
bucketMGI = set(mgiLookup)

# read in all annotations that contains MGD or GO or PMID

db.sql('''
        select a._Term_key, a._Object_key, e._AnnotEvidence_key, e.inferredFrom, t.abbreviation as evidenceCode, 
                m.symbol, aa.accid as goID, c.pubmedID
        into temporary table annotations 
        from VOC_Annot a, VOC_Evidence e, VOC_Term t, MRK_Marker m, ACC_Accession aa, BIB_Citation_Cache c
        where a._AnnotType_key = 1000 
        and a._Annot_key = e._Annot_key 
        and a._Object_key = m._Marker_key
        and e.inferredFrom is not null 
        and (e.inferredFrom like '%MGI%' or e.inferredFrom like '%GO%' or e.inferredFrom like '%PMID%')
        and e._EvidenceTerm_key = t._Term_key
        and a._Term_key = aa._Object_key
        and aa._MGIType_key = 13
        and aa.preferred = 1
        and e._Refs_key = c._Refs_key
        ''', None)

#
# set of MGI, GO ids, PMIDs in 'inferredFrom'
#

results = db.sql('''select _AnnotEvidence_key, inferredFrom, symbol, evidenceCode, goID, pubmedID  from annotations''', 'auto')

# {realid:[list of infoStrings], ...}
inferredLookup = {}
keysLookup = []
for r in results:
    ids = r['inferredFrom']
    key = r['_AnnotEvidence_key']
    # for potential reporting:
    symbol = r['symbol']
    evidenceCode = r['evidenceCode']
    goID = r['goID']
    if r['pubmedID'] != None:
        pubmedID = r['pubmedID']
    else:
        pubmedID = ""
    infoString = '%s%s%s%s%s%s%s%s' % (goID, reportlib.TAB, evidenceCode, reportlib.TAB, symbol, reportlib.TAB, pubmedID, reportlib.CRT)

    #print('ids: %s' % ids)
    #print('key: %s' % key)
    # any of these delimiters may be used
    ids = ids.replace(',', '|')
    ids = ids.replace(', ', '|')
    ids = ids.replace(';', '|')
    idList = str.split(ids, '|')
    #print('idList: %s' % idList)

    for id in idList:
        # save id as-is to check for lowercase/uppercase variations
        realid = id
        id.replace('"', '')
        id = id.upper()
        #print('realid: %s id: %s' % (realid, id))
        if str.find(id, 'MGI:') >= 0 or str.find(id, 'GO:') >= 0 or str.find(id, 'PMID:') >= 0:
           if realid not in inferredLookup:
              #print('realid added to inferredLookup: %s' % realid)
              if realid not in inferredLookup: 
                  inferredLookup[realid] = []
              inferredLookup[realid].append(infoString)
              keysLookup.append(key)

#
# bucket of all inferred-from ids
#

bucketInferred = set(inferredLookup.keys())
#print('bucketInferred: %s' % bucketInferred)

#
# compare inferred-from ids to MGI ids
#

theDiffs = bucketInferred.difference(bucketMGI)
#print('theDiffs: %s' % theDiffs)
row = 0
for t in theDiffs:

   infoList = inferredLookup[t]
   for s in infoList:
        fp.write(t + reportlib.TAB + s)
        rows = rows + 1

#
# include list of inferred-from values that contain ';'
#

results = db.sql('''
        select distinct aa.accID, m.symbol, t.term, e.inferredFrom, c.pubmedID
        from VOC_Annot a, VOC_Evidence e, VOC_Term t, ACC_Accession aa, MRK_Marker m, BIB_Citation_Cache c
        where a._AnnotType_key = 1000 
        and a._Annot_key = e._Annot_key 
        and e.inferredFrom like '%;%'
        and e._EvidenceTerm_key = t._Term_key
        and t._Term_key = aa._Object_key 
        and aa._MGIType_key = 13 
        and aa.preferred = 1 
        and a._Object_key = m._Marker_key 
        and e._Refs_key = c._Refs_key
        ''', 'auto')

for r in results:
    fp.write(r['inferredFrom'] + reportlib.TAB + \
             r['accID'] + reportlib.TAB + \
             r['symbol'] + reportlib.TAB)
    if r['pubmedID'] != None:
             fp.write(r['pubmedID'])
    fp.write(reportlib.CRT)

fp.write('\n(%d rows affected)\n' % (rows + len(results)))
reportlib.finish_nonps(fp)

