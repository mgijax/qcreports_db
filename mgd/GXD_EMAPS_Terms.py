#!/usr/local/bin/python

'''
#
# Report:
#       See TR11578 
#
# History:
#
# lec	01/08/2016
#	- TR12223/gxd anatomy II
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

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

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

# get EMAPS ID, TS and term name 
results = db.sql('''select t._Term_key, t.term, a.accid as emapsID, tt.stage
    from VOC_Term t, ACC_Accession a, VOC_Term_EMAPS emaps, GXD_TheilerStage tt
    where t._Vocab_key = 91
    and t._Term_key = a._Object_key
    and a._MGIType_key = 13
    and a._LogicalDB_key = 170
    and t._Term_key = emaps._Term_key
    and emaps._Stage_key = tt._Stage_key
    order by t.term, tt.stage''', 'auto')

numResults = len(results)
# write report
fp.write('EMAPS ID%sTerm%sStage%sSynonyms%s' % (TAB, TAB, TAB, CRT))
for r in results:
    termKey = r['_Term_key']
    term = r['term']
    emapsId = r['emapsID']
    stage = r['stage']
    synList = []
    if emapsSynDict.has_key(termKey):
	synList =  emapsSynDict[termKey]
    synString = '|'.join(synList)
    fp.write('%s%s%s%s%s%s%s%s' % (emapsId, TAB, term, TAB, stage, TAB, synString, CRT))
fp.write('%sTotal results: %s' % (CRT, numResults))

reportlib.finish_nonps(fp)	# non-postscript file
