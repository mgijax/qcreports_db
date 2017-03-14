#!/usr/local/bin/python

'''
#
# MRK_PRO_NoGO.py 
#
# Report:
#
#	TR12489 Papers selected for PRO, but not used in a GO/Marker annotation
#
#	Report in a tab delimited/html file with the following columns:
#
#	J: of reference associated with a Marker, where reference not used in a GO annotation
#	JNum
#	Marker MGI:ID
#
# Usage:
#       MRK_PRO_NoGO.py
#
# Notes:
#
# History:
#
# sc	02/15/2017
#	- TR12489 - new qc for papers triaged for PRO
#
'''
 
import sys
import os
import string
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

db.useOneConnection(1)
db.setTrace()

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)
# get refs used for GO
db.sql('''select distinct e._Refs_key
    into temporary table goUsed
    from VOC_Annot a, VOC_Evidence e
    where a._AnnotType_key = 1000 
    and a._Annot_key = e._Annot_key''', None)

db.sql('''create index idx1 on goUsed(_Refs_key)''', None)

# get marker references 
db.sql('''select v.jnumID, v._Refs_Key, a.accid as markerID
into temporary table markers
    from MGI_Reference_Marker_view v, ACC_Accession a
    where v._Refs_key in (236447, 238453, 238765, 239391,239667, 239714, 239754, 239758)
    and v._MGIType_key = 2 
    and v._Object_key = a._Object_key
    and a._MGIType_key = 2
    and a._LogicalDB_key = 1
    and a.preferred = 1
    and a.prefixPart = 'MGI:' ''', None)

db.sql('''create index idx2 on markers(_Refs_key)''', None)

# get the refs selected for PRO
db.sql('''select a.accid as jnumID, bda._Refs_key
into temporary table proRefs
    from BIB_DataSet_Assoc bda, ACC_Accession a
    where bda._DataSet_key = 1012 
    and bda._Refs_key = a._Object_key
    and a._MGIType_key = 1 
    and a._LogicalDB_key = 1
    and a.prefixPart = 'J:'
    and a.preferred = 1''', None)

db.sql('''create index idx3 on proRefs(_Refs_key)''', None)

# get the refs selected for GO 
db.sql('''select a.accid as jnumID, bda._Refs_key
    into temporary table goRefs
    from BIB_DataSet_Assoc bda, ACC_Accession a
    where bda._DataSet_key = 1005 
    and bda._Refs_key = a._Object_key
    and a._MGIType_key = 1 
    and a._LogicalDB_key = 1
    and a.prefixPart = 'J:'
    and a.preferred = 1''', None)

db.sql('''create index idx4 on goRefs(_Refs_key)''', None)

# get refs selected for PRO and GO
db.sql('''select p.* 
    into temporary table goProRefs
    from goRefs g, proRefs p
    where g._Refs_key = p._Refs_key''', None)

db.sql('''create index idx5 on goProRefs(_Refs_key)''', None)

# select refs selected for PRO and GO, but not used by GO 
db.sql('''select p.*
    into temporary table notUsed
    from goProRefs p
    where not exists (select 1
    from goUsed u
    where  p._Refs_key = u._Refs_key)''', None)

db.sql('''create index idx6 on notUsed(_Refs_key)''', None)

# final query, get markers if there are any
results = db.sql('''select distinct nu.jnumID, m.markerID
    from notUsed nu
    left outer join markers m on (nu._Refs_key = m._Refs_key)''', 'auto')

jNumDict = {}
print results
for r in results:
    jNumID = r['jnumID']
    markerID = r['markerID']
    if markerID == None:
	markerID = ''
    if jNumID not in jNumDict:
	jNumDict[jNumID] = []
    jNumDict[jNumID].append(markerID)

for j in jNumDict:
	fp.write('%s%s%s%s' % (j, TAB, string.join(jNumDict[j], ', '), CRT))

db.useOneConnection(0)

reportlib.finish_nonps(fp)
