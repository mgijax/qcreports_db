#!/usr/local/bin/python

'''
#
# Report:
#       See TR11578 
#
# History:
#
# lec   07/17/2014
#       - TR11708/remove seconday ids
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
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fp = reportlib.init(sys.argv[0], 'EMAPA Terms', os.environ['QCOUTPUTDIR'], printHeading = None)

emapaSynDict = {} # {termKey:[list of synonyms], ...}
# EMAPA
# EMAPA synonyms
results = db.sql('''select t._Term_key, s.synonym
    from VOC_Term t, MGI_Synonym s
    where t._Vocab_key = 90
    and t._Term_key = s._Object_key
    and s._MGIType_key = 13''', 'auto')

for r in results:
    termKey = r['_Term_key']
    synonym = r['synonym']
    if not emapaSynDict.has_key(termKey):
	emapaSynDict[termKey] = []
    emapaSynDict[termKey].append(synonym)

# get EMAPA ID, TS and term name 
results = db.sql('''select t._Term_key, t.term, a.accid as emapaID, 
	emapa.startStage, emapa.endStage
    from VOC_Term t, ACC_Accession a, VOC_Term_EMAPA emapa
    where t._Vocab_key = 90
    and t._Term_key = a._Object_key
    and a._MGIType_key = 13
    and a._LogicalDB_key = 169
    and a.preferred = 1
    and t._Term_key = emapa._Term_key
    order by t.term''', 'auto')

numResults = len(results)
# write report
fp.write('EMAPA ID%sTerm%sStage Range%sSynonyms%s' % (TAB, TAB, TAB, CRT))
for r in results:
    termKey = r['_Term_key']
    term = r['term']
    emapaId = r['emapaID']
    start = r['startStage']
    end = r['endStage']
    range = '%s, %s' % (start, end)
    synList = []
    if emapaSynDict.has_key(termKey):
	synList =  emapaSynDict[termKey]
    synString = '|'.join(synList)
    fp.write('%s%s%s%s%s%s%s%s' % (emapaId, TAB, term, TAB, range, TAB, synString, CRT))
fp.write('%sTotal results: %s' % (CRT, numResults))

reportlib.finish_nonps(fp)	# non-postscript file

