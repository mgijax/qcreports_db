#!/usr/local/bin/python

'''
#
# PRB_Strain6.py
#
# Report:
#       Tab-delimited file
#       Strains containing "either" or "invovles" and are standard
#
# Used by:
#       Internal Report
#
# Notes:
#
# History:
#
# 11/02/2006	lec
#	- TR 7983
#
'''
 
import sys
import os
import string
import mgi_utils
import reportlib
import db

db.setTrace()

TAB = reportlib.TAB
CRT = reportlib.CRT

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], title = 'Strains containing "either" or "involves" and marked STANDARD')

results = db.sql('''
	select s.strain 
	from PRB_Strain s 
	where s.standard = 1 
	and (s.strain like '%either%' or s.strain like '%involves%')
	''', 'auto')

for r in results:
    fp.write(r['strain'] + CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)

