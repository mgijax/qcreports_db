#!/usr/local/bin/python

'''
#
# TR 7298
#
# Report:
#       A report of alleles that have Associated Phenotype Controlled Terms
#       in the general notes field.
#
#	Allele Symbol
#	MP Annotation Indicator (yes/no)
#
# Usage:
#       ALL_AssocPheno.py
#
# Notes:
#
# History:
#
# 12/05/2005	lec
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

fp = reportlib.init(sys.argv[0], 'Alleles w/ "Associated Phenotype Controlled Terms" in Notes', os.environ['QCOUTPUTDIR'])
fp.write(string.ljust('symbol', 65) + string.ljust('annotation', 10) + CRT)
fp.write(string.ljust('------', 65) + string.ljust('---------', 10) + CRT)

db.sql('select a._Allele_key, a.symbol, nc.note, nc.sequenceNum ' + \
	'into #allele ' + \
	'from ALL_Allele a, MGI_Note n, MGI_NoteType nt, MGI_NoteChunk nc ' + \
	'where a._Allele_key = n._Object_key ' + \
	'and n._MGIType_key = 11 ' + \
	'and n._NoteType_key = nt._NoteType_key ' + \
	'and nt.noteType = "General" ' + \
	'and n._Note_key = nc._Note_key ', None)

results = db.sql('select * from #allele order by _Allele_key, sequenceNum', 'auto')
notes = {}
for r in results:
    key = r['_Allele_key']
    value = r['note']
    if not notes.has_key(key):
	notes[key] = []
    notes[key].append(value)

db.sql('create index idx1 on #allele(_Allele_key)', None)

results = db.sql('select distinct a._Allele_key, a.symbol, annotation = "no " ' + \
    'from #allele a ' + \
    'where not exists (select 1 from GXD_AlleleGenotype g, VOC_Annot v ' + \
    'where a._Allele_key = g._Allele_key ' + \
    'and g._Genotype_key = v._Object_key ' + \
    'and v._AnnotType_key = 1002) ' + \
    'union ' + \
    'select distinct a._Allele_key, a.symbol, annotation = "yes" ' + \
    'from #allele a ' + \
    'where exists (select 1 from GXD_AlleleGenotype g, VOC_Annot v ' + \
    'where a._Allele_key = g._Allele_key ' + \
    'and g._Genotype_key = v._Object_key ' + \
    'and v._AnnotType_key = 1002) ' + \
    'order by a.symbol', 'auto')

rows = 0
for r in results:
    key = r['_Allele_key']
    alleleNote = string.join(notes[key],'')
    if string.find(alleleNote, 'Associated Phenotype Controlled Terms') >= 0:
        fp.write(string.ljust(r['symbol'], 65) + string.ljust(r['annotation'], 10) + CRT)
	rows = rows + 1

fp.write(CRT + '(%d rows affected)' % rows + CRT)

reportlib.finish_nonps(fp)
