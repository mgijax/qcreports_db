#!/usr/local/bin/python

'''
#
# PRB_Strain2.py 08/07/2002
#
# Report:
#       Tab-delimited file
#       All Strains
#
# Usage:
#       PRB_Strain2.py
#
# Used by:
#       Internal Report
#
# Notes:
#
# History:
#
# lec	08/07/2002
#	- TR 3965
#
'''
 
import sys
import os
import string
import db
import mgi_utils
import reportlib

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCREPORTOUTPUTDIR'], printHeading = 0)

# Retrieve all Strains

cmd = 'select _Strain_key, strain, standard from PRB_Strain order by strain'
results = db.sql(cmd, 'auto')

for r in results:

	fp.write(r['strain'] + reportlib.TAB)

	if r['standard'] == 1:
		fp.write('Y' + reportlib.CRT)
	else:
		fp.write('N' + reportlib.CRT)

reportlib.finish_nonps(fp)

