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

db.useOneConnection(1)
fp = reportlib.init(sys.argv[0], 'Crosses Where # of Haplotypes Does Not Match # of Loci', os.environ['QCREPORTOUTPUTDIR'])
fp.write('J#' + TAB + 'Expt Type' + TAB + 'Tag' + CRT * 2)

# all experiments

cmds = []
cmds.append('select _Expt_key, alleleLine from MLD_MCDatalist ' + \
	'into #expts ' + \
	'where alleleLine not like "%par%" ' + \
	'and alleleLine not like "%reco%" ' + \
	'order by _Expt_key, sequenceNum')
cmds.append('create index idx1 on #expts(_Expt_key)')
db.sql(cmds, None)

# experiment details to print

results = db.sql('select _Expt_key, jnum, exptType, tag from #expts e, MLD_Expt_View ev ' + \
			'where e._Expt_key = ev._Expt_key', 'auto')
printRecs = {}
for r in results:
    key = r['_Expt_key']
    value = r
    printRecs[key] = r

# loci counts for each experiment

results = db.sql('select e._Expt_key, loci = count(em.*) from #expts e, MLD_Expt_Marker em ' + \
	'where e._Expt_key = em._Expt_key and matrixData = 1', 'auto')
loci = []
for r in results:
    key = r['_Expt_key']
    value = r['loci']
    loci[key] = value

results = db.sql('select _Expt_key, alleleLine from #expts', 'auto')

for r in results:
	row = string.splitfields(r['alleleLine'], ' ')
	columns = len(row)

	if exptKey != r['_Expt_key']:
		exptKey = r['_Expt_key']
		numLoci = loci[exptKey]
		printed = 0

	if columns == numLoci:
		continue

	if printed == 0:
		d = printRecs[exptKey]
		fp.write(`d['jnum']` + TAB + d['exptType'] + TAB + `d['tag']` + CRT)
		printed = 1

reportlib.trailer(fp)
reportlib.finish_nonps(fp)
db.useOneConnection(0)

