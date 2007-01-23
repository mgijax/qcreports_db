#!/usr/local/bin/python

'''
#
# Report:
#       Tab-delimited file of MGI Representative Genomic Sequences
#	(TR 8121)
#
#   1. MGI Marker ID
#   2. Marker Type
#   3. Marker Symbol
#   4. Marker Name
#   5. EntrezGene ID
#   6. Ensemlb ID
#   7. VEGA ID
#   8. Other Representative ID
#
# Usage:
#       MGI_RepSequences.py
#
# History:
#
# 01/23/2007 lec
#	- created
#
'''
 
import sys
import os
import string
import db
import reportlib
import mgi_utils

CRT = reportlib.CRT
TAB = reportlib.TAB

ncbi = 59
ensembl = 60
vega = 85

# Main
#

db.useOneConnection(1)
fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

# markers with representative genomic sequences

results = db.sql('select m.symbol, m.name, markerType = mt.name, mgiID = a.accID, smc._LogicalDB_key, smc.accID ' + \
        'from MRK_Marker m, MRK_Types mt, ACC_Accession a, SEQ_Marker_Cache smc ' + \
        'where m._Organism_key = 1 ' + \
	'and m._Marker_Status_key in (1,3) ' + \
	'and m._Marker_Type_key = mt._Marker_Type_key ' + \
	'and m._Marker_key = a._Object_key ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1 ' + \
	'and m._Marker_key = smc._Marker_key ' + \
	'and smc._Qualifier_key = 615419 ' + \
	'order by m.symbol ', 'auto')

for r in results:

    fp.write(r['mgiID'] + TAB)
    fp.write(r['markerType'] + TAB)
    fp.write(r['symbol'] + TAB)
    fp.write(r['name'] + TAB)

    if r['_LogicalDB_key'] == ncbi:
	fp.write(r['accID'] + 3*TAB + CRT)
    elif r['_LogicalDB_key'] == ensembl:
	fp.write(TAB + r['accID'] + 2*TAB + CRT)
    elif r['_LogicalDB_key'] == vega:
	fp.write(2*TAB + r['accID'] + TAB + CRT)
    else:
	fp.write(3*TAB + r['accID'] + CRT)

reportlib.finish_nonps(fp)
db.useOneConnection(0)

