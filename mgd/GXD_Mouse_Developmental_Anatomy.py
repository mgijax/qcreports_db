#!/usr/local/bin/python

'''
#
# Report:
#       TR11589, start with TR10542 and add system
#	Export Anatomical Dictionary to tab-delim and obo format
#	Tab-delim
#	1. MGI id of structure term
#	2. term name ('Stage' + stageKey (stage nodes) or 'TS' + 
#		stageKey + printName)
#	3. MGI id of parent term
#	4. parent term name ('Stage' + stageKey (stage nodes) or 
#		'TS' + stageKey + printName in reverse)
#	5. EMAP ID ('EMAP:' + edinburghKey)
#	6. synonyms (GXD_StructureName.structure where 
#		GXD_Structure._Structure_key = 	GXD_StructureName._Structure_key
#		 and GXD_Structure._StructureName_key  !=
#		GXD_StructureName._StructureName_key
#	7. anatomical system
#		
#
#	Export Anatomical Dictionary to tab-delim  format
#
# History:
#
# lec	03/11/2014
#	- TR11597/
#
# sc 02/10/2014
#	- added to QC reports
#
# sc 01/30/2014
#	- started with tr10542 and added system 
#
# sc	01/25/2011
#	- created
#
'''
 
import sys 
import os
import reportlib
import string
import db

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

db.useOneConnection(1)

# tab delim file
fp1 = reportlib.init(sys.argv[0], 'Anatomical Dictionary Terms', os.environ['QCOUTPUTDIR'])

# {structureKey:name, ...}
structureNameDict = {}

# {structureKey:synonym, ...}
synonymNameDict = {}

# {structureKey: mgiID}
mgiIdDict = {}

# Theiler Stage prefix
tsPrefix = 'TS'

# Stage prefix (structure name of stage nodes)
stagePrefix = 'Stage'

# EMAP ID prefix
emapPrefix = 'EMAP:'

# root node info
rootKey = ''
# note that this accID doesn't actually exist? (lec/3/11/2014)
rootID = 'MGI:4880586'
rootName = 'mouse developmental anatomy'

# write out column header
fp1.write('Structure Key%sStructure MGI ID%sStructure Term%sParent MGI ID%sParent Term%sEMAP ID%sSynonyms%sSystem%s%s' % (TAB, TAB, TAB, TAB, TAB, TAB, TAB, CRT, CRT))

# write the root node to tab-delim
fp1.write('%s%s%s%s%s%s%s%s%s%s' % (rootKey, TAB, rootID, TAB, rootName, TAB , TAB, TAB, TAB, CRT))

# select MGI IDs for structures and load lookup
results = db.sql('''select accid, _Object_key as _Structure_key
    from ACC_Accession
    where _MGIType_key = 38
    and _LogicalDB_key = 1
    and prefixPart = 'MGI:'
    and preferred = 1''', 'auto')

for r in results:
    mgiIdDict[r['_Structure_key']] = r['accid']

# select the print name and load lookup
results =  db.sql('''select _Structure_key, printName
    from GXD_Structure''', 'auto')
for r in results:
    structureKey = r['_Structure_key']
    structureNameDict[structureKey] = r['printName']

# select synonyms for structures and load lookup
results = db.sql('''select distinct s._Structure_key, sn.structure
    from GXD_Structure s, GXD_StructureName sn
    where s._Structure_key = sn._Structure_key
    and s._StructureName_key != sn._StructureName_key''', 'auto')

for r in results:
    structureKey = r['_Structure_key']
    if not synonymNameDict.has_key(structureKey):
	synonymNameDict[structureKey] = []
    synonymNameDict[structureKey].append(r['structure'])

# select all the structures and iterate through them
results =  db.sql('''select s._Structure_key, s._Parent_key,
    s.edinburghKey, s._Stage_key, s.printName, t.term as systemTerm
    from GXD_Structure s, VOC_Term t
    where s._System_key = t._Term_key
    order by s._Structure_key''', 'auto')

for r in results:

    structureKey = r['_Structure_key']
    parentKey = r['_Parent_key']
    edinburghKey = r['edinburghKey']
    stageKey = r['_Stage_key']
    structureID = mgiIdDict[structureKey]
    system = r['systemTerm']

    if parentKey == None:
	parentID = ''
    else:
	parentID = mgiIdDict[parentKey]

    structureName = r['printName']
    parentName = ''

    if structureNameDict.has_key(parentKey): 
	parentName = structureNameDict[parentKey]

    # If we have a stage node we'll need to convert 1-9
    # do it once now rather than twice later (structure AND parent)
    sKey = stageKey
    if sKey in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
	sKey = '0%s' % sKey

    # is this a stage node?
    if structureName == ' ':
	structureName = '%s%s' % (stagePrefix, sKey)
	parentName = rootName
	parentID = rootID
    else:
	structureName = '%s%s,%s' % \
	    (tsPrefix, stageKey, structureName)

    if parentName == ' ':
	parentName = '%s%s' % (stagePrefix, sKey)

    elif parentName != '' and parentName != rootName:
        parentName = '%s%s,%s' % \
            (tsPrefix, stageKey, parentName)

    synonyms = ''
    synonymList = []

    if synonymNameDict.has_key(structureKey):
        synonymList = synonymNameDict[structureKey]
        synonyms = string.join(synonymList, ',')
    emapID = ''

    if edinburghKey != None:
        emapID = '%s%s' % (emapPrefix, edinburghKey)
    # write to tab delim report

    fp1.write('%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' \
	% (structureKey, TAB, structureID, TAB, structureName, TAB, parentID, \
		TAB, parentName, TAB, emapID, TAB, synonyms, TAB, system, CRT))
    
db.useOneConnection(0)
reportlib.finish_nonps(fp1)
