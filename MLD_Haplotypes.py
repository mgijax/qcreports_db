#!/usr/local/bin/python

'''
#
# MLD_Haplotypes.py 11/16/98
#
# Report:
# 	Print out all Mapping Experiments where the number of loci 
#	in an experiment's locus list does not equal the number of 
#	columns in the haplotype matrix
#
# Usage:
#       MLD_Haplotypes.py
#
# Generated from:
#       on demand
#
# History:
#
# lec	01/13/98
#	- added comments
#
'''
 
import sys
import os
import string
import posix
import db
import reportlib

CRT = reportlib.CRT
TAB = reportlib.TAB

exptKey = None
numLoci = 0
printed = 0

fp = reportlib.init(sys.argv[0], 'Crosses Where # of Haplotypes Does Not Match # of Loci', os.environ['QCREPORTOUTPUTDIR'])
fp.write('J#' + TAB + 'Expt Type' + TAB + 'Tag' + CRT * 2)

command = 'select _Expt_key, alleleLine from MLD_MCDatalist ' + \
	'where alleleLine not like "%par%" ' + \
	'and alleleLine not like "%reco%" ' + \
	'order by _Expt_key, sequenceNum'
results = db.sql(command, 'auto')

for r in results:
	row = string.splitfields(r['alleleLine'], ' ')
	columns = len(row)

	if exptKey != r['_Expt_key']:
		exptKey = r['_Expt_key']
		numLoci = 0
		printed = 0

		cmd = 'select loci = count(*) from MLD_Expt_Marker ' + \
			'where _Expt_key = %d and matrixData = 1' % exptKey
		lociList = db.sql(cmd, 'auto')
		for l in lociList:
			numLoci = l['loci']

	if columns == numLoci:
		continue

	if printed == 0:
		cmd = 'select jnum, exptType, tag from MLD_Expt_View ' + \
			'where _Expt_key = %d' % exptKey
		detailList = db.sql(cmd, 'auto')
		for d in detailList:
			fp.write(`d['jnum']` + TAB + d['exptType'] + TAB + `d['tag']` + CRT)
			printed = 1

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

