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
db.sql('''select distinct e._Refs_key
    into temporary table gorefs
    from VOC_Annot a, VOC_Evidence e
    where a._AnnotType_key = 1000 /* GO */
    and a._Annot_key = e._Annot_key''', None)
db.sql('create index idx1 on gorefs(_Refs_key)', None)

results = db.sql('''select v.jnumID, a.accid as markerID
    from BIB_DataSet_Assoc bda, MGI_Reference_Marker_view v, ACC_Accession a
    where bda._DataSet_key = 1012 /* PRO */
    and bda._Refs_key = v._Refs_key
    and v._MGIType_key = 2 /* Marker */
    and v._Object_key = a._Object_key
    and a._MGIType_key = 2
    and a._LogicalDB_key = 1
    and a.preferred = 1
    and a.prefixPart = 'MGI:'
    and not exists (select 1 /* not used in GO annotation */
    from gorefs g
    where bda._Refs_key = g._Refs_key)''', 'auto')

jNumDict = {}
for r in results:
    jNumID = r['jnumID']
    markerID = r['markerID']
    if jNumID not in jNumDict:
	jNumDict[jNumID] = []
    jNumDict[jNumID].append(markerID)

for j in jNumDict:
	fp.write('%s%s%s%s' % (j, TAB, string.join(jNumDict[j], ', '), CRT))

db.useOneConnection(0)

reportlib.finish_nonps(fp)
