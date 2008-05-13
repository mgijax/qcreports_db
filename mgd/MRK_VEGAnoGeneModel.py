#!/usr/local/bin/python

'''
#
# Report:
#
#	VEGA Genes with no VEGA Gene Model Association
#
#       Produce a tab-delimited report with the following output fields:
#
#       1) MGI ID
#       2) Gene Symbol
#	3) Gene Model ID (if one exists by same name)
#
# Usage:
#
# 	MRK_VEGAnoGeneModel.py	
#
'''
 
import sys 
import os
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#
fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

fp.write('#%s' % CRT)
fp.write('# VEGA Genes with no VEGA Gene Model Association%s' % CRT)
fp.write('#%s' % CRT)
fp.write('MGI ID%sGene Symbol%sHas GM by same name%s' % (TAB, TAB, CRT))

# get the full set of VEGA gene model ids
results = db.sql('select accID ' + \
    'from ACC_Accession  a, SEQ_Sequence s ' + \
    'where a._LogicalDB_key = 85 ' + \
    'and a._MGIType_key = 19 ' + \
    'and a._Object_key = s._Sequence_key', 'auto')

geneModelList = []
for r in results:
    geneModelList.append(r['accID'])

# get the set of VEGA markers with VEGA gene model associations
results = db.sql('select distinct m.symbol ' + \
    'from ACC_Accession a, MRK_Marker m ' + \
    'where a._LogicalDB_key = 85 ' + \
    'and a._MGIType_key = 2 ' + \
    'and a.preferred = 1 ' + \
    'and a._Object_key = m._Marker_key ' + \
    'and m.symbol like "OTTMUSG%" ' + \
    'and m._Marker_Status_key = 1', 'auto')

geneAssocList = []
for r in results:
    geneAssocList.append(r['symbol'])

# get the list of official VEGA Markers and their MGI ids
results = db.sql('select a.accID as MGIid, m.symbol ' + \
    'from ACC_Accession a, MRK_Marker m ' + \
    'where a._MGIType_key = 2 ' + \
    'and a._LogicalDB_key = 1 ' + \
    'and a.preferred = 1 ' + \
    'and a._Object_key = m._Marker_key ' + \
    'and m.symbol like "OTTMUSG%" ' + \
    'and m._Marker_Status_key = 1' + \
    'order by m.symbol ' , 'auto')

ctr = 0
for r in results:
    symbol = r['symbol']
    if symbol not in geneAssocList:
	hasModel = 'no'
        if symbol in geneModelList:
	    hasModel = 'yes'
	fp.write('%s%s%s%s%s%s' % (r['MGIid'], TAB, symbol, TAB, hasModel, CRT))
	ctr= ctr + 1
fp.write('total = %s' % ctr)
reportlib.finish_nonps(fp)
