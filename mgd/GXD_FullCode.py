#!/usr/local/bin/python

'''
#
# TR 6469
#
# Report:
#
# Usage:
#       GXD_FullCode.py
#
# Notes:
#
# History:
#
# lec	01/12/2005
#	- converted GXD_DevBiol.sql, GXD_Development.sql, GXD_MechDev.sql, GXD_GeneExprPatterns.sql to one report
#	- added Dev Dyn
#
'''

import sys
import os
import string
import regsub
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

journals = ['Dev Biol', 'Dev Dyn', 'Development', 'Mech Dev', 'Gene Expr Patterns']

natureJournals = ['Cell Death Differ', 'Oncogene', 'Nature', 'Nat Cell Biol', 'Nat Genet', 'Nat Immunol', 'Nat Med', 'Nat Neurosci', 'Nat Struct Biol', 'Nat Biotechnol', 'Biotechnology', 'Nat Rev Cancer', 'Nat Rev Genet', 'Nat Rev Immunol', 'Nat Rev Mol Cell Bio', 'Nat Rev Neurosci']

def processJournal(jList, fileName, journalTitle):

    fp = reportlib.init(fileName, outputdir = os.environ['QCOUTPUTDIR'])

    fp.write('Reference and Number of Markers Analyzed for Journal: %s' % (journalTitle) + 2*CRT)
    fp.write(string.ljust('accID', 30))
    fp.write(SPACE)
    fp.write(string.ljust('markerCount', 12))
    fp.write(SPACE)
    fp.write(CRT)
    fp.write(string.ljust('-----', 30))
    fp.write(SPACE)
    fp.write(string.ljust('-----------', 12))
    fp.write(SPACE)
    fp.write(CRT)

    # get set of references not coded with high priority

    db.sql('select distinct i._Refs_key, i._Marker_key ' + \
           'into #markers1 ' + \
           'from GXD_Index i, BIB_Refs b, VOC_Term_GXDIndexPriority_View a ' + \
           'where i._Refs_key = b._Refs_key ' + \
	   'and b.journal in ("' + string.join(jList, '","') + '") ' + \
           'and i._Priority_key =  a._Term_key ' + \
           'and a.term = "High" ' + \
           'and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key)', None)

    db.sql('create index idx1 on #markers1(_Refs_key)', None)
    db.sql('select m.*, markerCount = count(*) into #mcount1 from #markers1 m group by _Refs_key', None)
    db.sql('create index idx1 on #mcount1(_Refs_key)', None)

    results = db.sql('select distinct a.accID, i.markerCount ' + \
                     'from #mcount1 i, ACC_Accession a ' + \
                     'where i._Refs_key = a._Object_key ' + \
                     'and a._MGIType_key = 1 ' + \
                     'and a.prefixPart = "J:" ' + \
                     'order by markerCount desc', 'auto')

    for r in results:
	fp.write(string.ljust(r['accID'], 30))
	fp.write(SPACE)
	fp.write(string.ljust(str(r['markerCount']), 12))
	fp.write(SPACE)
	fp.write(CRT)
    fp.write('\n(%d rows affected)\n' % (len(results)))

    #
    # new genes
    #

    fp.write(CRT)
    fp.write('%s:  Papers with New Genes' % (journalTitle) + 2*CRT)
    fp.write(string.ljust('accID', 30))
    fp.write(SPACE)
    fp.write(string.ljust('markerCount', 12))
    fp.write(SPACE)
    fp.write(CRT)
    fp.write(string.ljust('-----', 30))
    fp.write(SPACE)
    fp.write(string.ljust('-----------', 12))
    fp.write(SPACE)
    fp.write(CRT)

    # get set of references/markers not coded with high priority

    db.sql('select distinct i._Refs_key, i._Marker_key ' + \
           'into #markers2 ' + \
           'from GXD_Index i, BIB_Refs b, VOC_Term_GXDIndexPriority_View a ' + \
           'where i._Refs_key = b._Refs_key ' + \
	   'and b.journal in ("' + string.join(jList, '","') + '") ' + \
           'and i._Priority_key =  a._Term_key ' + \
           'and a.term = "High" ' + \
           'and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key) ' + \
           'and not exists (select 1 from GXD_Assay a where i._Marker_key = a._Marker_key) ', None)

    db.sql('create index idx1 on #markers2(_Refs_key)', None)
    db.sql('select m.*, markerCount = count(*) into #mcount2 from #markers2 m group by _Refs_key', None)
    db.sql('create index idx1 on #mcount2(_Refs_key)', None)

    results = db.sql('select distinct a.accID, i.markerCount ' + \
                     'from #mcount2 i, ACC_Accession a ' + \
                     'where i._Refs_key = a._Object_key ' + \
                     'and a._MGIType_key = 1 ' + \
                     'and a.prefixPart = "J:" ' + \
                     'order by markerCount desc', 'auto')

    for r in results:
	fp.write(string.ljust(r['accID'], 30))
	fp.write(SPACE)
	fp.write(string.ljust(str(r['markerCount']), 12))
	fp.write(SPACE)
	fp.write(CRT)
    fp.write('\n(%d rows affected)\n' % (len(results)))

    reportlib.trailer(fp)
    reportlib.finish_nonps(fp)

#
# Main
#

for j in journals:
    jList = []
    jList.append(j)
    fileName = 'GXD_' + regsub.gsub(' ', '', j)
    processJournal(jList, fileName, j)

fileName = 'GXD_Nature'
processJournal(natureJournals, fileName, 'Nature')

