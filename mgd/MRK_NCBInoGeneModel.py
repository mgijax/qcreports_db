#!/usr/local/bin/python

'''
#
# TR 8966
#
# Report:
#
#	NCBI Genes with no NCBI Gene Model Association
#
#       Produce a tab-delimited report with the following output fields:
#
#       1) MGI ID
#       2) Gene Symbol
#	3) Gene Model ID (if one exists by same name)
#
# Usage:
#
# 	MRK_NCBInoGeneModel.py	
#
# lec	05/08/2008
#	- TR 8966; Build 37
#	copied from MRK_ENSEMBLnoGeneModel
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
print "initializing"
fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

fp.write('#%s' % CRT)
fp.write('# NCBI Genes with no NCBI Gene Model Association%s' % CRT)
fp.write('#%s' % CRT)
fp.write('MGI ID%sGene Symbol%sHas GM by same name%s' % (TAB, TAB, CRT))

# get the full set of NCBI gene model ids
results = db.sql('select accID ' + \
    'from ACC_Accession  a, SEQ_Sequence s ' + \
    'where a._LogicalDB_key = 59 ' + \
    'and a._MGIType_key = 19 ' + \
    'and a._Object_key = s._Sequence_key', 'auto')

geneModelList = []
for r in results:
    geneModelList.append(r['accID'])

# get the set of NCBI markers with NCBI gene model associations
results = db.sql('select distinct m.symbol ' + \
    'from ACC_Accession a, MRK_Marker m ' + \
    'where a._LogicalDB_key = 59 ' + \
    'and a._MGIType_key = 2 ' + \
    'and a.preferred = 1 ' + \
    'and a._Object_key = m._Marker_key ' + \
    'and m.name like "predicted gene, EG%" ' + \
    'and m._Marker_Status_key = 1', 'auto')

geneAssocList = []
for r in results:
    geneAssocList.append(r['symbol'])

# get the full set of NCBI Markers
results = db.sql('select a.accID as MGIid, m.symbol ' + \
    'from ACC_Accession a, MRK_Marker m ' + \
    'where a._MGIType_key = 2 ' + \
    'and a._LogicalDB_key = 1 ' + \
    'and a.preferred = 1 ' + \
    'and a._Object_key = m._Marker_key ' + \
    'and m.name like "predicted gene, EG%" ' + \
    'and m._Marker_Status_key = 1' + \
    'order by m.symbol', 'auto')

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
