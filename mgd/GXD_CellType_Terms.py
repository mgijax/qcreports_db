
'''
#
# Report:
#   GXD_CellType_Terms.rpt       
#
# History:
#
# sc    10/29/2021 
#       created for YAKS project cell types
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

fp = reportlib.init(sys.argv[0], 'CellType Terms', os.environ['QCOUTPUTDIR'], printHeading = None)

synDict = {} # {termKey:[list of synonyms], ...}

# CellType terms that have synonyms
results = db.sql('''select t._Term_key, s.synonym
    from VOC_Term t, MGI_Synonym s
    where t._Vocab_key = 102
    and t._Term_key = s._Object_key
    and s._MGIType_key = 13''', 'auto')

for r in results:
    termKey = r['_Term_key']
    synonym = r['synonym']
    if termKey not in synDict:
        synDict[termKey] = []
    synDict[termKey].append(synonym)

# get CellType ID and term
results = db.sql('''select t._Term_key, t.term, a.accid
    from VOC_Term t, ACC_Accession a
    where t._Vocab_key = 102
    and t.isobsolete = 0
    and t._Term_key = a._Object_key
    and a._MGIType_key = 13
    and a._LogicalDB_key = 173
    and a.preferred = 1
    order by t.term''', 'auto')

numResults = len(results)
# write report
fp.write('CellType ID%sTerm%sSynonyms%s' % (TAB, TAB, CRT))
for r in results:
    termKey = r['_Term_key']
    term = r['term']
    celltypeId = r['accid']
    synList = []
    if termKey in synDict:
        synList =  synDict[termKey]
    synString = '|'.join(synList)
    fp.write('%s%s%s%s%s%s' % (celltypeId, TAB, term, TAB, synString, CRT))
fp.write('%sTotal results: %s' % (CRT, numResults))

reportlib.finish_nonps(fp)	# non-postscript file
