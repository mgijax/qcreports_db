#!/usr/local/bin/python

'''
#
# Tissue.py 11/16/98
#
# Report:
#	Basic Tissue Info
#
# Usage:
#       Tissue.py
#
# Generated from:
#       Editing Interface Tissues Form
#
# Notes:
#
# History:
#
# lec	06/12/1998
#	- created
#
'''
 
import sys
import os
import string
import regsub
import mgdlib
import reportlib

CRT = reportlib.CRT
SP = reportlib.SPACE
fp = None

tissues = mgdlib.sql(sys.argv[1], 'auto')

for s in tissues:

	if fp is None:  
		reportName = regsub.gsub(' ', '', s['tissue'])
		reportName = regsub.gsub('/', '', reportName)
		reportName = 'Tissue.%s.rpt' % reportName
		fp = reportlib.init(reportName, 'Tissues', os.environ['QCREPORTOUTPUTDIR'])

	results = mgdlib.sql('PRB_getTissueDataSets %s' % s['_Tissue_key'], 'auto')

	prevTissue = ''

	for r in results:

		if prevTissue != s['tissue']:
			fp.write(2 * CRT)
			fp.write('Tissue: %s' % s['tissue'])
			fp.write(2*CRT)
			fp.write(string.ljust('DataSet', 20))
			fp.write('Accession #')
			fp.write(CRT)
			fp.write(string.ljust('-------', 20))
			fp.write('-----------')
			fp.write(CRT)
			prevTissue = s['tissue']

		else:
			fp.write(CRT + string.ljust(r['dataSet'], 20))
			fp.write(r['accID'])

reportlib.finish_nonps(fp)

