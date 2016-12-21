#!/usr/local/bin/python

'''
#
# GO_InvalidInferredFrom.py
#
# Report:
#       
# GO curators can use an evidence code of IC for an annotation and use a GO id in 
# the WITH/inferred_from field.
#
# However, sometimes an id becomes secondary or is obsoleted. We currently have 
# to check on this, as this field is a text field.
#
# Therefore, it would be helpful to have a QC run that checks annotations with 
# evidence code IC for a valid GO id.

# field 1: MGI ID
# field 2: MGI symbol
# field 3: Annotation that has the IC
# field 4: Contents of WITH field if found invalid.
#
# Usage:
#       GO_InvalidInferredFrom.py
#
# History:
#
# 10/24/2016	sc
#	- TR11840
#
'''
 
import sys 
import os
import string
import reportlib
import db
import re

db.setTrace()
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#

# from database
# {goId:[preferred1, preferred2], ...}
goDict = {}

# generate GO ID lookup of all GO IDs preferred and not preferred
results = db.sql('''
	select a.accid, a.preferred
	from ACC_Accession a
	where a._MGIType_key = 13
	and a._LogicalDB_key = 31''', 'auto')
for r in results:
    goId = r['accid']
    preferred = r['preferred']
    if goId not in goDict:
	goDict[goId] = []
    goDict[goId].append(preferred)

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)
fp.write('MGI-ID' + TAB)
fp.write('MGI symbol' + TAB)
fp.write('Annotation that has the IC' + TAB)
fp.write('Invalid ID in WITH field' + TAB)
fp.write('Primary ID' + CRT)

#
# select all GO annotations with IC evidence
#
results = db.sql('''
	select va._Annot_key, va._Object_key, va._Term_key, va.accid as goId,  ve.inferredFrom, m.symbol, a.accid as mgiId
	from VOC_Annot_View va, VOC_Evidence ve, MRK_Marker m, ACC_Accession a
	where va._AnnotType_key = 1000
	and va._Annot_key = ve._Annot_key
	and ve._EvidenceTerm_key = 25238 /* IC*/
	and va._Object_key = m._Marker_key
	and va._Object_key = a._Object_key
	and a._MGIType_key = 2
	and a._LOgicalDB_key = 1
	and a.preferred = 1
	and a.prefixPart = 'MGI:'
	''', 'auto')

invalidList = []
for r in results:
    goId = r['goId']
    mgiId = r['mgiId']
    symbol = r['symbol']
    inferredFrom = r['inferredFrom']
    for id in re.split(r'[;,\|]\s*', inferredFrom):
	if id not in goDict:
	    invalidList.append('%s%s%s%s%s%s%s%sNot in database%s' % (mgiId, TAB, symbol, TAB, goId, TAB, inferredFrom, TAB, CRT))
	else:
	    preferredList = goDict[id]
	    if 0 in preferredList:
		results = db.sql('''select distinct a2.accid
		    from ACC_Accession a1, ACC_Accession a2
		    where a1.accid = 'GO:2000898'
		    and a1._MGIType_key = 13
		    and a1._LogicalDB_key = 31
		    and a1.preferred = 0
		    and a1._Object_key = a2._Object_key
		    and a2._MGIType_key = 13
		    and a2._LogicalDB_key = 31
		    and a2.preferred = 1''', 'auto')
		primaryIdList = []
		for r in results:
		    primaryIdList.append(r['accid'])
		invalidList.append('%s%s%s%s%s%s%s%s%s%s' % (mgiId, TAB, symbol, TAB, goId, TAB, inferredFrom, TAB, string.join(primaryIdList, ', '), CRT))

for i in invalidList:
    fp.write(i)
reportlib.finish_nonps(fp)

