#!/usr/local/bin/python

'''
#
# TR 6703
#
# Report:
#       Produce a report of alleles that have Molecular Notes
#       but no Molecular Mutation.
#
#       MGI ID of Allele
#	Allele Symbol
#	Allele Type
#	Molecular Note
#
# Usage:
#       ALL_NoMolMutation.py
#
# Notes:
#
# History:
#
# 04/01/2005	lec
#       - created
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

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Alleles that have Molecular Notes but no Molecular Mutation', os.environ['QCOUTPUTDIR'])

db.sql('select a._Allele_key into #alleles ' + \
	'from ALL_Allele a, VOC_Term t ' + \
	'where a._Allele_Type_key = t._Term_key ' + \
		'and t.term != "QTL" ' + \
		'and exists (select 1 from MGI_Note n, MGI_NoteType nt ' + \
		'where a._Allele_key = n._Object_key ' + \
		'and n._MGIType_key = 11 ' + \
		'and n._NoteType_key = nt._NoteType_key ' + \
		'and nt.noteType = "Molecular") ' + \
	'and not exists (select 1 from ALL_Allele_Mutation m where a._Allele_key = m._Allele_key)', None)

db.sql('create index idex1 on #alleles(_Allele_key)', None)

results = db.sql('select a._Allele_key, nc.note ' + \
	'from #alleles a, MGI_Note n, MGI_NoteType nt, MGI_NoteChunk nc ' + \
	'where a._Allele_key = n._Object_key ' + \
	'and n._MGIType_key = 11 ' + \
	'and n._NoteType_key = nt._NoteType_key ' + \
	'and nt.noteType = "Molecular" ' + \
	'and n._Note_key = nc._Note_key ' + \
	'order by a._Allele_key, nc.sequenceNum', 'auto')
notes = {}
for r in results:
    key = r['_Allele_key']
    value = r['note']
    if not notes.has_key(key):
	notes[key] = []
    notes[key].append(value)

results = db.sql('select a._Allele_key, ac.accID, aa.symbol, alleleType = t.term ' + \
	'from #alleles a, ACC_Accession ac, ALL_Allele aa, VOC_Term t ' + \
	'where a._Allele_key = ac._Object_key ' + \
        'and ac._MGIType_key = 11 ' + \
        'and ac._LogicalDB_key = 1 ' + \
        'and ac.prefixPart = "MGI:" ' + \
        'and ac.preferred = 1 ' + \
	'and a._Allele_key = aa._Allele_key ' + \
	'and aa._Allele_Type_key = t._Term_key ' + \
        'order by ac.numericPart', 'auto')

for r in results:
        fp.write(r['accID'] + TAB + \
		 r['symbol'] + TAB + \
		 r['alleleType'] + TAB + \
		 string.join(notes[r['_Allele_key']], '') + CRT)

fp.write(CRT + 'Number of Alleles: ' + str(len(results)) + CRT)

reportlib.finish_nonps(fp)
