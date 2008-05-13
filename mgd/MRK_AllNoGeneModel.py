#!/usr/local/bin/python

'''
#
# Report:
#
#	Ensembl/VEGA/NCBI Genes with Gene Model Association to different providers
#
#       Produce a tab-delimited report with the following output fields:
#
#       1) MGI ID
#       2) Gene Symbol
#	3) Gene Model ID (if one exists by same name)
#
# Usage:
#
# 	MRK_AllNoGeneModel.py	
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
fp.write('# Ensembl/VEGA/NCBI Genes with Gene Model Association to different providers%s' % CRT)
fp.write('#%s' % CRT)
fp.write('MGI ID%sGene Symbol%sGene Model ID of different type than symbol%s' % (TAB, TAB, CRT))

#
# command to select markers/accession ids/gene model associations
#

cmd = 'select m.symbol, g.accID, mgiID = a.accID ' + \
    'from MRK_Marker m, ACC_Accession g, ACC_Accession a, ACC_Accession gm ' + \
    'where m._Organism_key = 1 ' + \
    'and m._Marker_Status_key = 1' + \
    'and m._Marker_key = g._Object_key ' + \
    'and g._MGIType_key = 2 ' + \
    'and g._Object_key = gm._Object_key ' + \
    'and gm._MGIType_key = 19 ' + \
    'and m._Marker_key = a._Object_key ' + \
    'and a._MGIType_key = 2 ' + \
    'and a._LogicalDB_key = 1 ' + \
    'and a.preferred = 1 '

# ensembl markers with vega/ncbi associations
results = db.sql(cmd + 
    'and m.symbol like "ENSMUSG%" ' + \
    'and g._LogicalDB_key in (59, 85) ' + 
    'order by g.accID', 'auto')

fp.write(CRT)
for r in results:
    fp.write(r['mgiID'] + TAB)
    fp.write(r['symbol'] + TAB)
    fp.write(r['accID'] + CRT)
fp.write('\n(%d rows affected)\n' % (len(results)))

# ncbi markers with ensembl/vega associations
results = db.sql(cmd + 
    'and m.name like "predicted gene, EG%" ' + \
    'and g._LogicalDB_key in (60, 85) ' + 
    'order by g.accID', 'auto')

fp.write(CRT)
for r in results:
    fp.write(r['mgiID'] + TAB)
    fp.write(r['symbol'] + TAB)
    fp.write(r['accID'] + CRT)
fp.write('\n(%d rows affected)\n' % (len(results)))

# vega markers with ensembl/ncbi associations
results = db.sql(cmd + 
    'and m.symbol like "OTTMUSG%" ' + \
    'and g._LogicalDB_key in (59, 60) ' + 
    'order by g.accID', 'auto')

fp.write(CRT)
for r in results:
    fp.write(r['mgiID'] + TAB)
    fp.write(r['symbol'] + TAB)
    fp.write(r['accID'] + CRT)
fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.finish_nonps(fp)
