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

	# for each marker/go ID, print one row in the output file
	# each row will contain the unique list of evidence codes
	# used for those marker/go ID annotations

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

fpA = reportlib.init("MRK_GOGold_A", printHeading = 0, outputdir = os.environ['QCOUTPUTDIR'])
fpA.write('mgi ID' + TAB + \
	 'symbol' + TAB + \
	 'name' + TAB + \
	 'DAG abbreviation' + TAB + \
	 'GO ID' + TAB + \
	 'GO Term' + TAB + \
	 'evidence codes' + CRT*2)

fpB = reportlib.init("MRK_GOGold_B", printHeading = 0, outputdir = os.environ['QCOUTPUTDIR'])
fpB.write('mgi ID' + TAB + \
	 'symbol' + TAB + \
	 'name' + TAB + \
	 'DAG abbreviation' + TAB + \
	 'GO ID' + TAB + \
	 'GO Term' + TAB + \
	 'evidence codes' + CRT*2)


fpC = reportlib.init("MRK_GOGold_C", printHeading = 0, outputdir = os.environ['QCOUTPUTDIR'])
fpC.write('mgi ID' + TAB + \
	 'symbol' + TAB + \
	 'name' + TAB + \
	 'DAG abbreviation' + TAB + \
	 'GO ID' + TAB + \
	 'GO Term' + TAB + \
	 'evidence codes' + CRT*2)


fpD = reportlib.init("MRK_GOGold_D", printHeading = 0, outputdir = os.environ['QCOUTPUTDIR'])
fpD.write('mgi ID' + TAB + \
	 'symbol' + TAB + \
	 'name' + TAB + \
	 'DAG abbreviation' + TAB + \
	 'GO ID' + TAB + \
	 'GO Term' + TAB + \
	 'evidence codes' + CRT*2)

# select mouse genes, annotations where evidence code = IDA, IGI, IMP, IPI, TAS
cmds = []
cmds.append('select m._Marker_key, m.symbol, m.name, a.term, goID = a.accID, e.evidenceCode, d.abbreviation ' + \
	'into #m1 ' + \
	'from MRK_Marker m, VOC_Annot_View a, VOC_Evidence_View e, VOC_VocabDAG vd, DAG_Node n, DAG_DAG d ' + \
	'where m._Organism_key = 1 ' + \
	'and m._Marker_Type_key = 1 ' + \
	'and m._Marker_Status_key in (1,3) ' + \
	'and m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e.evidenceCode in ("IDA", "IGI", "IMP", "IPI", "TAS") ' + \
	'and a._Vocab_key = vd._Vocab_key ' +
	'and vd._DAG_key = n._DAG_key ' + \
	'and a._Term_key = n._Object_key ' + \
	'and n._DAG_key = d._DAG_key '
	'order by m.symbol')
cmds.append('create index idx1 on #m1(_Marker_key)')
db.sql(cmds, None)

# select mouse genes, annotations where evidence code = IDA, IGI, IMP, IPI
cmds = []
cmds.append('select m._Marker_key, m.symbol, m.name, a.term, goID = a.accID, e.evidenceCode, d.abbreviation ' + \
	'into #m2 ' + \
	'from MRK_Marker m, VOC_Annot_View a, VOC_Evidence_View e, VOC_VocabDAG vd, DAG_Node n, DAG_DAG d ' + \
	'where m._Organism_key = 1 ' + \
	'and m._Marker_Type_key = 1 ' + \
	'and m._Marker_Status_key in (1,3) ' + \
	'and m._Marker_key = a._Object_key ' + \
	'and a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e.evidenceCode in ("IDA", "IGI", "IMP", "IPI") ' + \
	'and a._Vocab_key = vd._Vocab_key ' +
	'and vd._DAG_key = n._DAG_key ' + \
	'and a._Term_key = n._Object_key ' + \
	'and n._DAG_key = d._DAG_key '
	'order by m.symbol')
cmds.append('create index idx1 on #m2(_Marker_key)')
db.sql(cmds, None)

# select MGI accession ids for mouse genes from set 1
# this will also suffice for set 2 which is a subset of set 1

results = db.sql('select distinct m._Marker_key, ma.accID ' + \
	'from #m1 m, ACC_Accession ma ' + \
	'where m._Marker_key = ma._Object_key ' + \
	'and ma._MGIType_key = 2 ' + \
	'and ma.prefixPart = "MGI:" ' + \
	'and ma._LogicalDB_key = 1 ' + \
	'and ma.preferred = 1 ', 'auto')
accid = {}
for r in results:
	accid[r['_Marker_key']] = r['accID']

## Report A

results = db.sql('select * from #m1', 'auto')
for r in results:
	writeRecord1(fpA, r)

## Report B

results = db.sql('select * from #m2', 'auto')
for r in results:
	writeRecord1(fpB, r)

## Report C

# select all records from set 1 which have multiple annotations to the same GO term
cmds = []
cmds.append('select * into #m3 from #m1 group by _Marker_key, goID having count(*) > 1')
cmds.append('create index idx1 on #m3(_Marker_key)')
cmds.append('create index idx2 on #m3(symbol)')
db.sql(cmds, None)

# select distinct marker, GO ID, evidence code from set 1 annotations
# we're doing this because for a given marker/go ID we only want to print
# one row in the output file which will contain the list of unique evidence codes
# used for that marker/go ID annotation
# store dictionary of evidence cods by marker/go ID
results = db.sql('select distinct _Marker_key, goID, evidenceCode from #m3', 'auto')
ecode = {}
for r in results:
	key = `r['_Marker_key']` + ':' + r['goID']
	if not ecode.has_key(key):
		ecode[key] = []
	ecode[key].append(r['evidenceCode'])

results = db.sql('select distinct _Marker_key, symbol, name, term, goID, abbreviation from #m3 order by symbol', 'auto')
for r in results:
	writeRecord2(fpC, r)

## Report D

# select all records from set 2 which have multiple annotations to the same GO term
cmds = []
cmds.append('select * into #m4 from #m2 group by _Marker_key, goID having count(*) > 1')
cmds.append('create index idx1 on #m4(_Marker_key)')
cmds.append('create index idx2 on #m4(symbol)')
db.sql(cmds, None)

# select distinct marker, GO ID, evidence code from set 2 annotations
results = db.sql('select distinct _Marker_key, goID, evidenceCode from #m4', 'auto')
ecode = {}
for r in results:
	key = `r['_Marker_key']` + ':' + r['goID']
	if not ecode.has_key(key):
		ecode[key] = []
	ecode[key].append(r['evidenceCode'])

results = db.sql('select distinct _Marker_key, symbol, name, term, goID, abbreviation from #m4 order by symbol', 'auto')
for r in results:
	writeRecord2(fpD, r)

reportlib.finish_nonps(fpA)	# non-postscript file
reportlib.finish_nonps(fpB)	# non-postscript file
reportlib.finish_nonps(fpC)	# non-postscript file
reportlib.finish_nonps(fpD)	# non-postscript file

