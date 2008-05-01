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
# lec	05/01/2008
#	- TR 8775; on select GXD assay types
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

journals = ['Cell Death Differ', 'Oncogene', 'Nature', 'Nat Cell Biol', 'Nat Genet', 'Nat Immunol', 'Nat Med', 'Nat Neurosci', 'Nat Struct Biol', 'Nat Biotechnol', 'Biotechnology', 'Nat Rev Cancer', 'Nat Rev Genet', 'Nat Rev Immunol', 'Nat Rev Mol Cell Bio', 'Nat Rev Neurosci']

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Papers Requiring Permissions', outputdir = os.environ['QCOUTPUTDIR'])

fp.write(TAB + 'where publication year >= 2002' + CRT*2)

fp.write(TAB + 'Journals Checked:' + CRT)
for j in journals:
    fp.write(2*TAB + j + CRT)
fp.write(CRT)
fp.write(TAB + string.ljust('J#', 12))
fp.write(string.ljust('short_citation', 75))
fp.write(string.ljust('figure labels', 50) + CRT)
fp.write(TAB + string.ljust('--', 12))
fp.write(string.ljust('--------------', 75))
fp.write(string.ljust('-------------', 50) + CRT)

db.sql('select distinct r._Refs_key, r.journal, a.creation_date into #refs ' + \
	'from BIB_Refs r, GXD_Assay a ' + \
	'where r.year >= 2002 ' + \
	'and r.journal in ("' + string.join(journals, '","') + '") ' + \
	'and r._Refs_key = a._Refs_key ' + \
	'and a._AssayType_key not in (10,11) ' + \
	'and exists (select 1 from IMG_Image a where r._Refs_key = a._Refs_key and xDim is null)', None)
db.sql('create index idx1 on #refs(_Refs_key)', None)

results = db.sql('select distinct r._Refs_key, figureLabel = rtrim(i.figureLabel) ' + \
	'from #refs r, IMG_Image i ' + \
	'where r._Refs_key = i._Refs_key', 'auto')
fLabels = {}
for r in results:
    key = r['_Refs_key']
    value = r['figureLabel']
    if not fLabels.has_key(key):
	fLabels[key] = []
    fLabels[key].append(value)

results = db.sql('select r._Refs_key, b.jnumID, b.short_citation from #refs r, BIB_All_View b ' + \
	'where r._Refs_key = b._Refs_key order by r.creation_date, b.jnumID', 'auto')

refprinted = []
for r in results:
    if r['_Refs_key'] not in refprinted:
        fp.write(TAB + string.ljust(r['jnumID'], 12))
        fp.write(string.ljust(r['short_citation'], 75))
        fp.write(string.ljust(string.join(fLabels[r['_Refs_key']], ','), 50) + CRT)
	refprinted.append(r['_Refs_key'])

fp.write(CRT + 'Total J numbers: ' + str(len(results)) + CRT)

reportlib.finish_nonps(fp)
