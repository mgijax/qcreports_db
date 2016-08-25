#!/usr/local/bin/python

'''
#
# MRK_GOGold.py 06/07/2002
#
# Report:
#       TR 3763 - remove A(1), C(3)
#
#    	Report 2
#	Title = All Genes with Annotation to IDA, IGI, IMP, IPI
#	Select markers of type 'gene' 
#		where evidence code = IDA, IGI, IMP, IPI
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
# lec	12/31/2009
#	- TR9989; remove A(1), C(3)
#
# lec	07/08/2008
#	- TR8945
#
# lec	06/07/2002
#	- created
#
'''
 
import sys 
import os
import string
import reportlib
import db

db.setTrace()
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

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

fpB = reportlib.init("MRK_GOGold_B", printHeading = None, outputdir = os.environ['QCOUTPUTDIR'])
fpB.write('mgi ID' + TAB + \
	 'symbol' + TAB + \
	 'name' + TAB + \
	 'DAG abbreviation' + TAB + \
	 'GO ID' + TAB + \
	 'GO Term' + TAB + \
	 'evidence codes' + CRT*2)

fpD = reportlib.init("MRK_GOGold_D", printHeading = None, outputdir = os.environ['QCOUTPUTDIR'])
fpD.write('mgi ID' + TAB + \
	 'symbol' + TAB + \
	 'name' + TAB + \
	 'DAG abbreviation' + TAB + \
	 'GO ID' + TAB + \
	 'GO Term' + TAB + \
	 'evidence codes' + CRT*2)

# select mouse genes, annotations where evidence code = IDA, IGI, IMP, IPI, TAS
db.sql('''
	select m._Marker_key, m.symbol, m.name, a.term, a.accID as goID, e.evidenceCode, d.abbreviation 
	into temporary table m1 
	from MRK_Marker m, VOC_Annot_View a, VOC_Evidence_View e, VOC_VocabDAG vd, DAG_Node n, DAG_DAG d 
	where m._Organism_key = 1 
	and m._Marker_Type_key = 1 
	and m._Marker_Status_key = 1
	and m._Marker_key = a._Object_key 
	and a._AnnotType_key = 1000 
	and a._Annot_key = e._Annot_key 
	and e.evidenceCode in ('IDA', 'IGI', 'IMP', 'IPI', 'TAS') 
	and a._Vocab_key = vd._Vocab_key 
	and vd._DAG_key = n._DAG_key 
	and a._Term_key = n._Object_key 
	and n._DAG_key = d._DAG_key 
	order by m.symbol
	''', None)
db.sql('create index m1_idx1 on m1(_Marker_key)', None)

# select mouse genes, annotations where evidence code = IDA, IGI, IMP, IPI
db.sql('''
	select m._Marker_key, m.symbol, m.name, a.term, a.accID as goID, e.evidenceCode, d.abbreviation, a._annot_key 
	into temporary table m2 
	from MRK_Marker m, VOC_Annot_View a, VOC_Evidence_View e, VOC_VocabDAG vd, DAG_Node n, DAG_DAG d 
	where m._Organism_key = 1 
	and m._Marker_Type_key = 1 
	and m._Marker_Status_key = 1
	and m._Marker_key = a._Object_key 
	and a._AnnotType_key = 1000 
	and a._Annot_key = e._Annot_key 
	and e.evidenceCode in ('IDA', 'IGI', 'IMP', 'IPI') 
	and a._Vocab_key = vd._Vocab_key 
	and vd._DAG_key = n._DAG_key 
	and a._Term_key = n._Object_key 
	and n._DAG_key = d._DAG_key 
	order by m.symbol
	''', None)
db.sql('create index m2_idx1 on m2(_Marker_key)', None)
db.sql('create index m2_idx_goid on m2(goID)', None)
db.sql('create index m2_idx_annot_key on m2(_annot_key)', None)

# select MGI accession ids for mouse genes from set 1
# this will also suffice for set 2 which is a subset of set 1

results = db.sql('''
	select distinct m._Marker_key, ma.accID 
	from m1 m, ACC_Accession ma 
	where m._Marker_key = ma._Object_key 
	and ma._MGIType_key = 2 
	and ma.prefixPart = 'MGI:' 
	and ma._LogicalDB_key = 1 
	and ma.preferred = 1 
	''', 'auto')
accid = {}
for r in results:
	accid[r['_Marker_key']] = r['accID']

## Report B

# number of unique MGI gene
results = db.sql('select distinct _Marker_key from m2', 'auto')
fpB.write('Number of unique MGI Gene IDs:  %s\n' % (len(results)))

# total number of rows
results = db.sql('select * from m2', 'auto')
fpB.write('Total number of rows:  %s\n\n' % (len(results)))

results = db.sql('select * from m2', 'auto')
for r in results:
	writeRecord1(fpB, r)

## Report D

# select all records from set 2 which have multiple annotations to the same GO term
db.sql('''select * into temporary table m4 from m2 m2_1
	where exists (select 1 from m2 m2_2 
		where m2_1._marker_key = m2_2._marker_key
			and m2_1.goID = m2_2.goID
			and m2_1._annot_key != m2_2._annot_key
	)''', None)
db.sql('create index m4_idx1 on m4(_Marker_key)', None)
db.sql('create index m4_idx2 on m4(symbol)', None)

# select distinct marker, GO ID, evidence code from set 2 annotations
results = db.sql('select distinct _Marker_key, goID, evidenceCode from m4', 'auto')
ecode = {}
for r in results:
	key = `r['_Marker_key']` + ':' + r['goID']
	if not ecode.has_key(key):
		ecode[key] = []
	ecode[key].append(r['evidenceCode'])

# number of unique MGI gene
results = db.sql('select distinct _Marker_key from m4', 'auto')
fpD.write('Number of unique MGI Gene IDs:  %s\n' % (len(results)))

# total number of rows
results = db.sql('select * from m4', 'auto')
fpD.write('Total number of rows:  %s\n\n' % (len(results)))

results = db.sql('select distinct _Marker_key, symbol, name, term, goID, abbreviation from m4 order by symbol', 'auto')
for r in results:
	writeRecord2(fpD, r)

reportlib.finish_nonps(fpB)	# non-postscript file
reportlib.finish_nonps(fpD)	# non-postscript file

