
'''
#
#	MRK_C4AM_GeneModel.py
#
# Report:
#       Weekly report of markers with curated coordinates associated 
#	  with gene models
#
# Usage:
#       MRK_C4AM_GeneModel.py
#
# Notes:
#	- all reports use mgireport directory for output file
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- use proper case for all table and column names e.g. 
#         use MRK_Marker not mrk_marker
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
#
# sc	07/06/2022
#	- created https://mgi-jira.atlassian.net/browse/CRM-306
#
'''
 
import sys 
import os
import string
import reportlib
import db

db.useOneConnection(1)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'QTL-to-Candidate Gene Relationships', os.environ['QCOUTPUTDIR'])

fp.write('QTL ID%sQTL symbol%sCandidate ID%sCandidate symbol%sJnum ID%s' % (TAB, TAB, TAB, TAB, CRT))

results = db.sql('''select a1.accid as qtlID, m1.symbol as qtlSymbol, 
        a2.accid as candidateKey, m2.symbol as candidateSymbol, a3.accid as jnumID
    from mgi_relationship r, acc_accession a1, acc_accession a2, acc_accession a3, mrk_marker m1, mrk_marker m2
    where r._category_key = 1009
    and r._object_key_1 = a1._object_key
    and a1._mgitype_key = 2
    and a1._logicaldb_key = 1
    and a1.prefixPart = 'MGI:'
    and a1.preferred = 1
    and r._object_key_2 = a2._object_key
    and a2._mgitype_key = 2
    and a2._logicaldb_key = 1
    and a2.prefixPart = 'MGI:'
    and a2.preferred = 1
    and r._refs_key = a3._object_key
    and a3._mgitype_key = 1
    and a3._logicaldb_key = 1
    and a3.prefixPart = 'J:'
    and a3.preferred = 1
    and r._object_key_1 = m1._marker_key
    and r._object_key_2 = m2._marker_key''', 'auto')


for r in results:
    qtlID = r['qtlID']
    qtlSymbol = r['qtlSymbol']
    candidateKey = r['candidateKey']
    candidateSymbol = r['candidateSymbol']
    jnumID = r['jnumID']

    fp.write('%s%s%s%s%s%s%s%s%s%s' % (qtlID, TAB, qtlSymbol, TAB, candidateKey, TAB, candidateSymbol, TAB, jnumID, CRT))

fp.write(CRT)
fp.write('Total: %s' % len(results))

db.useOneConnection(0)
reportlib.finish_nonps(fp)	# non-postscript file
