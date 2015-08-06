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

db.setTrace()
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)
db.useOneConnection(1)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE
reportlib.column_width = 150

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], fileExt = '.rpt', printHeading = None)

db.sql('''
	select r._Refs_key
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

results = db.sql('''
        select aRef.accID as jNum
        from selNotUsed s, ACC_Accession aRef
        where s._Refs_key = aRef._Object_key
        and aRef._MGIType_key = 1
        and aRef._LogicalDB_key = 1
        and aRef.prefixPart = 'J:'
        and aRef.preferred = 1
        order by aRef.accID''', 'auto')
notUsedSet = set([])
for r in results:
    jNum = r['jNum']
    notUsedSet.add(jNum)
fp.write("References selected for QTL and not used%s%s" % (CRT, CRT))
for j in notUsedSet:
    fp.write('%s%s' % (j, CRT))
fp.write('Total References selected and not used: %s' % len(notUsedSet))

db.useOneConnection(0)
reportlib.finish_nonps(fp)	# non-postscript file
