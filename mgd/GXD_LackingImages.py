#!/usr/local/bin/python

'''
#
# GXD_LackingImages.py
#
# Report:
#       Produce a report of all J numbers from the journals specified
#	that are full coded in GXD database but do not have images
#       attached to them.
#
# Usage:
#       GXD_LackingImages.py
#
# Notes:
#
# History:
#
# lec	01/13/2005
#	- TR 6480
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

journals = ['Dev Biol', 'Cell Death Differ', 'Oncogene', 'Nature', 'Nat Cell Biol', 'Nat Genet', 'Nat Immunol', 'Nat Med', 'Nat Neurosci', 'Nat Struct Biol', 'Nat Biotechnol', 'Biotechnology', 'Nat Rev Cancer', 'Nat Rev Genet', 'Nat Rev Immunol', 'Nat Rev Mol Cell Bio', 'Nat Rev Neurosci']

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Fully Coded Papers Lacking Images', outputdir = os.environ['QCOUTPUTDIR'])

fp.write(TAB + 'Journals Checked:' + CRT)
for j in journals:
    fp.write(2*TAB + j + CRT)
fp.write(CRT)
fp.write(TAB + 'J#' + TAB + 'short_citation' + CRT)
fp.write(TAB + '--' + TAB + '--------------' + CRT)

db.sql('select distinct r._Refs_key, r.journal into #refs ' + \
	'from BIB_Refs r, GXD_Index i ' + \
	'where r.journal in ("' + string.join(journals, '","') + '") ' + \
	'and r._Refs_key = i._Refs_key ' + \
	'and not exists (select 1 from GXD_Assay a where r._Refs_key = a._Refs_key)', None)
db.sql('create index idx1 on #refs(_Refs_key)', None)

results = db.sql('select b.jnumID, b.short_citation from #refs r, BIB_All_View b ' + \
	'where r._Refs_key = b._Refs_key order by r.journal, b.jnumID', 'auto')
for r in results:
	fp.write(TAB + r['jnumID'] + TAB + r['short_citation'] + CRT)

fp.write(CRT + 'Total J numbers: ' + str(len(results)) + CRT)

reportlib.trailer(fp)
reportlib.finish_nonps(fp)
