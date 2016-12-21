#!/usr/local/bin/python

'''
#
# QTL_Triage.py
#
# Report:
#       Weekly QTL Triage Report
#
# Usage:
#       QTL_Triage.py
#
# sc	08/31/2015
#	- TR12082 add markers
#
# sc   07/29/2015
#       - TR12082
#
'''
 
import sys 
import os
import mgi_utils
import reportlib
import Set
import db
import string

db.setTrace()
db.useOneConnection(1)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE
reportlib.column_width = 150

# QTL marker keys mapped to their symbol and MGI ID
qtlDict = {}

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], fileExt = '.rpt', printHeading = None)

results = db.sql('''select m._Marker_key, m.symbol, a.accID
	from MRK_Marker m, ACC_Accession a
	where m._Marker_Type_key = 6
	and m._Marker_Status_key = 1
	and m._Marker_key = a._Object_key
	and a._MGIType_key = 2
	and a._LogicalDB_key = 1
	and a.preferred = 1
	and a.prefixPart = 'MGI:' ''', 'auto')
for r in results:
    mrkKey = r['_Marker_key']
    symbol = r['symbol']
    mgiID = r['accID']
    if not qtlDict.has_key(mrkKey):
	qtlDict[mrkKey] = []
    qtlDict[mrkKey].append('%s, %s' % (symbol, mgiID))
db.sql('''
	select distinct r._Refs_key
	into temporary table selNotUsed
	from BIB_Refs r, BIB_DataSet_Assoc a
	where r._Refs_key = a._Refs_key
	and a._DataSet_key = 1011
	and not exists (
	select 1 from MLD_Expts m
	where m.exptType in ('TEXT', 'TEXT-QTL', 'TEXT-QTL-Candidate Genes', 'TEXT-Congenic', 'TEXT-Meta Analysis')
	and m._Refs_key = r._Refs_key)
	''', None)

db.sql('create index idx1 on selNotUsed(_Refs_key)', None)

db.sql('''
        select distinct s._Refs_key, aRef.accID as jNum
	into temporary table withJnum
        from selNotUsed s, ACC_Accession aRef
        where s._Refs_key = aRef._Object_key
        and aRef._MGIType_key = 1
        and aRef._LogicalDB_key = 1
        and aRef.prefixPart = 'J:'
        and aRef.preferred = 1''', None)

db.sql('create index idx2 on withJnum(_Refs_key)', None)

results = db.sql('''
	select distinct mr._Marker_key, j.*
	from withJnum j
	LEFT OUTER JOIN MRK_Reference mr on (j._Refs_key = mr._Refs_key)
	order by j.jNum
	''', 'auto')

distinctDict = {}
for r in results:
    mrkKey = r['_Marker_key']
    jNum = r['jNum']
    mrkList = []
    if mrkKey != None  and qtlDict.has_key(mrkKey):
	mrkList = qtlDict[mrkKey]
    if not distinctDict.has_key(jNum):
	distinctDict[jNum] = []
    markers = ''
    if mrkList != []:
	markers = string.join(mrkList, ' | ')
    if markers != '':
	distinctDict[jNum].append(markers)

fp.write("References selected for QTL and not used%s%s" % (CRT, CRT)) 
jNums = distinctDict.keys()
jNums.sort()
for jNum in jNums:
    fp.write('%s%s%s%s' % (jNum, TAB, string.join(distinctDict[jNum], ' | '), CRT))
fp.write('Total References selected and not used: %s' % len(jNums))

db.useOneConnection(0)
reportlib.finish_nonps(fp)	# non-postscript file
