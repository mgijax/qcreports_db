
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
import string
import Set
import mgi_utils
import reportlib
import db

db.setTrace()

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])
fp.write('\nInvalid "Inferred From" Values in GO Annotations (MGI, GO, ";")' + 2 * reportlib.CRT)
rows = 0

# read in all MGI accession ids for Markers (2), Alleles (11)
# read in all GO ids (13)
# this is the list of valid accession ids

mgiLookup = []
results = db.sql('select a.accID from ACC_Accession a where a._MGIType_key in (2, 11) and a.prefixPart = \'MGI:\'', 'auto')
for r in results:
    mgiLookup.append(r['accID'])
results = db.sql('select a.accID from ACC_Accession a where a._MGIType_key = 13 and a.prefixPart in (\'GO:\')', 'auto')
for r in results:
    mgiLookup.append(r['accID'])
bucketMGI = set(mgiLookup)

# read in all annotations that contains MGD or GO

db.sql('''
        select a._Term_key, a._Object_key, e._AnnotEvidence_key, e.inferredFrom, 
               t.abbreviation as evidenceCode
        into temporary table annotations 
        from VOC_Annot a, VOC_Evidence e, VOC_Term t 
        where a._AnnotType_key = 1000 
        and a._Annot_key = e._Annot_key 
        and e.inferredFrom is not null 
        and (e.inferredFrom like '%MGI%' or e.inferredFrom like '%GO%')
        and e._EvidenceTerm_key = t._Term_key
        ''', None)
db.sql('create index annotations_idx1 on annotations(_Term_key)', None)
db.sql('create index annotations_idx2 on annotations(_Object_key)', None)
db.sql('create index annotations_idx3 on annotations(inferredFrom)', None)

#
# set of MGI, GO ids in 'inferredFrom'
#

results = db.sql('select _AnnotEvidence_key, inferredFrom from annotations', 'auto')

inferredLookup = []
keysLookup = []
for r in results:
    ids = r['inferredFrom']
    key = r['_AnnotEvidence_key']

    # any of these delimiters may be used
    ids = ids.replace(',', '|')
    ids = ids.replace(', ', '|')
    ids = ids.replace(';', '|')
    idList = str.split(ids, '|')

    for id in idList:
        # save id as-is to check for lowercase/uppercase variations
        realid = id
        id.replace('"', '')
        id = id.upper()

        if str.find(id, 'MGI:') >= 0 or str.find(id, 'GO:') >= 0:
           if realid not in inferredLookup:
              inferredLookup.append(realid)
              keysLookup.append(key)

#
# bucket of all inferred-from ids
#

bucketInferred = set(inferredLookup)

#
# compare inferred-from ids to MGI ids
#

theDiffs = bucketInferred.difference(bucketMGI)

row = 0
for t in theDiffs:

   toSelect = '%' + t + '%'

   results = db.sql('''
        select a.accID, m.symbol, e.evidenceCode, e._AnnotEvidence_key
        from annotations e, ACC_Accession a, MRK_Marker m 
        where e._Term_key = a._Object_key 
        and a._MGIType_key = 13 
        and a.preferred = 1 
        and e._Object_key = m._Marker_key 
        and e.inferredFrom like '%s'
        ''' % (toSelect), 'auto')

   for r in results:
      key = r['_AnnotEvidence_key']
      if key in keysLookup:
          fp.write(t + reportlib.TAB + \
                   r['accID'] + reportlib.TAB + \
                   r['evidenceCode'] + reportlib.TAB + \
                   r['symbol'] + reportlib.CRT)
          rows = rows + 1

#
# include list of inferred-from values that contain ';'
#

results = db.sql('''
        select distinct aa.accID, m.symbol, t.term, e.inferredFrom
        from VOC_Annot a, VOC_Evidence e, VOC_Term t, ACC_Accession aa, MRK_Marker m
        where a._AnnotType_key = 1000 
        and a._Annot_key = e._Annot_key 
        and e.inferredFrom like '%;%'
        and e._EvidenceTerm_key = t._Term_key
        and t._Term_key = aa._Object_key 
        and aa._MGIType_key = 13 
        and aa.preferred = 1 
        and a._Object_key = m._Marker_key 
        ''', 'auto')

for r in results:
    fp.write(r['inferredFrom'] + reportlib.TAB + \
             r['accID'] + reportlib.TAB + \
             r['symbol'] + reportlib.CRT)

fp.write('\n(%d rows affected)\n' % (rows + len(results)))
reportlib.finish_nonps(fp)
