#!/usr/local/bin/python

'''
#
# Report:
#       See TR11578 
#
# History:
#
# sc	12/15/2014
#	- TR11749/use official structure name on GXD QC report
#
# lec	03/11/2014
#	- TR11597/make this a weekly report
#
# sc	01/28/2014
#	- created
#
'''
 
import sys 
import os
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

db.useOneConnection(1)

fp = reportlib.init(sys.argv[0], 'EMAPS Terms', os.environ['QCOUTPUTDIR'], printHeading = None)

emapsSynDict = {} # {termKey:[list of synonyms], ...}
# EMAPS
# EMAPS synonyms
results = db.sql('''select t._Term_key, s.synonym
    from VOC_Term t, MGI_Synonym s
    where t._Vocab_key = 91
    and t._Term_key = s._Object_key
    and s._MGIType_key = 13''', 'auto')
print 'len synonyms %s' % len(results)
for r in results:
    termKey = r['_Term_key']
    synonym = r['synonym']
    if not emapsSynDict.has_key(termKey):
	emapsSynDict[termKey] = []
    emapsSynDict[termKey].append(synonym)

# EMAPS mappings 1-1
mappingDict = {}
results = db.sql('''select mem.emapsId, mem.accId, gs.structure
	from MGI_EMAPS_Mapping mem, ACC_Accession a, GXD_StructureName gs, 
	    GXD_Structure g
	where mem.accId = a.accId
	and a._MGIType_key = 38
	and a._Object_key = gs._Structure_key
	and gs._StructureName_key = g._Structure_key''', 'auto')
for r in results:
    mappingDict[r['emapsId']] = [r['accId']]
    mappingDict[r['emapsId']].append(r['structure'])

# get EMAPS ID, TS and term name 
results = db.sql('''select t._Term_key, t.term, a.accid as emapsID, 
	emaps.stage
    from VOC_Term t, ACC_Accession a, VOC_Term_EMAPS emaps
    where t._Vocab_key = 91
    and t._Term_key = a._Object_key
    and a._MGIType_key = 13
    and a._LogicalDB_key = 170
    and t._Term_key = emaps._Term_key
    order by t.term''', 'auto')

numResults = len(results)
# write report
fp.write('EMAPS ID%sTerm%sStage%sSynonyms%sMapped AD ID%sMapped AD Term%s' % (TAB, TAB, TAB, TAB, TAB, CRT))
for r in results:
    termKey = r['_Term_key']
    term = r['term']
    emapsId = r['emapsID']
    stage = r['stage']
    synList = []
    adId = ''
    structureName = ''
    if mappingDict.has_key(emapsId):
	adId = mappingDict[emapsId][0]
	structureName = mappingDict[emapsId][1]
    if emapsSynDict.has_key(termKey):
	synList =  emapsSynDict[termKey]
    synString = '|'.join(synList)
    fp.write('%s%s%s%s%s%s%s%s%s%s%s%s' % (emapsId, TAB, term, TAB, stage, TAB, synString, TAB, adId, TAB, structureName, CRT))
fp.write('%sTotal results: %s' % (CRT, numResults))

reportlib.finish_nonps(fp)	# non-postscript file
db.useOneConnection(0)

