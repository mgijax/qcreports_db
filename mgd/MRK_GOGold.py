#!/usr/local/bin/python

'''
#
# MRK_GOGold.py 06/07/2002
#
# Report:
#       TR 3763 - Report 1
#
#	Report 1
#	Title = All Genes with Annotation to IDA, IGI, IMP, IPI, TAS
#	Select markers of type 'gene' 
#		where evidence code = IDA, IGI, IMP, IPI, TAS
#
#       Report in a tab delimited file with the following columns:
#
#    		MGI:ID
#    		symbol
#		name
#		DAG
#		GO ID
#		Term
#		Evidence Code
#
#    	Report 2
#	Title = All Genes with Annotation to IDA, IGI, IMP, IPI
#	Select markers of type 'gene' 
#		where evidence code = IDA, IGI, IMP, IPI
#
#	Report 3
#	Title = All Genes with > 1 Annotation to IDA, IGI, IMP, IPI, TAS
#	Select markers of type 'gene' 
#		where evidence code = IDA, IGI, IMP, IPI, TAS
#		where number of annoations > 1
#
#	Report 4
#	Title = All Genes with > 1 Annotation to IDA, IGI, IMP, IPI
#	Select markers of type 'gene' 
#		where evidence code = IDA, IGI, IMP, IPI
#		where number of annoations > 1
#
# Usage:
#       MRK_GOGold.py
#
# Notes:
#	- all reports use mgireport directory for output file
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
#
# lec	06/07/2002
#	- created
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

def writeRecord1(fp, r):

	fp.write(accid[r['_Marker_key']] + TAB + \
	         r['symbol'] + TAB + \
	         r['name'] + TAB + \
	         r['abbreviation'] + TAB + \
	         r['goID'] + TAB + \
	         r['term'] + TAB + \
	         r['evidenceCode'] + CRT)

def writeRecord2(fp, r):

	key = `r['_Marker_key']` + ':' + r['goID']

	fp.write(accid[r['_Marker_key']] + TAB + \
	         r['symbol'] + TAB + \
	         r['name'] + TAB + \
	         r['abbreviation'] + TAB + \
	         r['goID'] + TAB + \
	         r['term'] + TAB + \
		 string.joinfields(ecode[key], ',') + CRT)

#
# Main
#

fpA = reportlib.init("MRK_GOGold_A", printHeading = 0, outputdir = os.environ['QCREPORTOUTPUTDIR'])
fpB = reportlib.init("MRK_GOGold_B", printHeading = 0, outputdir = os.environ['QCREPORTOUTPUTDIR'])
fpC = reportlib.init("MRK_GOGold_C", printHeading = 0, outputdir = os.environ['QCREPORTOUTPUTDIR'])
fpD = reportlib.init("MRK_GOGold_D", printHeading = 0, outputdir = os.environ['QCREPORTOUTPUTDIR'])

cmds = []

cmds.append('select m._Marker_key, m.symbol, m.name, a.term, goID = a.accID, e.evidenceCode, d.abbreviation ' + \
'into #m1 ' + \
'from MRK_Marker m, VOC_Annot_View a, VOC_Evidence_View e, VOC_VocabDAG vd, DAG_Node n, DAG_DAG d ' + \
'where m._Species_key = 1 ' + \
'and m._Marker_Type_key = 1 ' + \
'and m._Marker_Status_key = 1 ' + \
'and m._Marker_key = a._Object_key ' + \
'and a._AnnotType_key = 1000 ' + \
'and a._Annot_key = e._Annot_key ' + \
'and e.evidenceCode in ("IDA", "IGI", "IMP", "IPI", "TAS") ' + \
'and a._Vocab_key = vd._Vocab_key ' +
'and vd._DAG_key = n._DAG_key ' + \
'and a._Term_key = n._Object_key ' + \
'and n._DAG_key = d._DAG_key '
'order by m.symbol')

cmds.append('select m._Marker_key, m.symbol, m.name, a.term, goID = a.accID, e.evidenceCode, d.abbreviation ' + \
'into #m2 ' + \
'from MRK_Marker m, VOC_Annot_View a, VOC_Evidence_View e, VOC_VocabDAG vd, DAG_Node n, DAG_DAG d ' + \
'where m._Species_key = 1 ' + \
'and m._Marker_Type_key = 1 ' + \
'and m._Marker_Status_key = 1 ' + \
'and m._Marker_key = a._Object_key ' + \
'and a._AnnotType_key = 1000 ' + \
'and a._Annot_key = e._Annot_key ' + \
'and e.evidenceCode in ("IDA", "IGI", "IMP", "IPI") ' + \
'and a._Vocab_key = vd._Vocab_key ' +
'and vd._DAG_key = n._DAG_key ' + \
'and a._Term_key = n._Object_key ' + \
'and n._DAG_key = d._DAG_key '
'order by m.symbol')

cmds.append('select distinct m._Marker_key, ma.accID ' + \
'from #m1 m, MRK_Acc_View ma ' + \
'where m._Marker_key = ma._Object_key ' + \
'and ma.prefixPart = "MGI:" ' + \
'and ma.preferred = 1 ')

cmds.append('select * from #m1')

cmds.append('select * from #m2')

cmds.append('select * into #m3 from #m1 group by _Marker_key, goID having count(*) > 1')

cmds.append('select distinct _Marker_key, goID, evidenceCode from #m3')

cmds.append('select distinct _Marker_key, symbol, name, term, goID, abbreviation from #m3 order by symbol')

cmds.append('select * into #m4 from #m2 group by _Marker_key, goID having count(*) > 1')

cmds.append('select distinct _Marker_key, goID, evidenceCode from #m4')

cmds.append('select distinct _Marker_key, symbol, name, term, goID, abbreviation from #m4 order by symbol')

results = db.sql(cmds, 'auto')

accid = {}
for r in results[2]:
	accid[r['_Marker_key']] = r['accID']

for r in results[3]:
	writeRecord1(fpA, r)

for r in results[4]:
	writeRecord1(fpB, r)

ecode = {}
for r in results[6]:
	key = `r['_Marker_key']` + ':' + r['goID']
	if not ecode.has_key(key):
		ecode[key] = []

	ecode[key].append(r['evidenceCode'])

for r in results[7]:
	writeRecord2(fpC, r)

ecode = {}
for r in results[9]:
	key = `r['_Marker_key']` + ':' + r['goID']
	if not ecode.has_key(key):
		ecode[key] = []

	ecode[key].append(r['evidenceCode'])

for r in results[10]:
	writeRecord2(fpD, r)

reportlib.finish_nonps(fpA)	# non-postscript file
reportlib.finish_nonps(fpB)	# non-postscript file
reportlib.finish_nonps(fpC)	# non-postscript file
reportlib.finish_nonps(fpD)	# non-postscript file

