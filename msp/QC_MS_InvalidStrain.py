#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of Invalid Strains
#       from QC_MS_InvalidStrain.
#
# Usage:
#       QC_MS_InvalidStrain.py
#
# Notes:
#
# History:
#
# lec   03/16/2004
#       - created
#
'''
 
import os
import sys 
import db
import string
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

outputDir = os.environ['OUTPUTDIR']
jobStreamKey = os.environ['JOBSTREAM']

fp = reportlib.init(sys.argv[0],  
		    'Molecular Source Processer - Invalid Strains (Job Stream %s)' % (jobStreamKey), 
		    outputdir = outputDir, sqlLogging = 0)

fp.write("  A row in this report represents a Strain that could not be translated to a valid MGI Strain.\n" + \
"  This Strain may need to be added to the Strain bad name/good name list.\n" + 2*CRT)

fp.write(string.ljust('Strain', 100))
fp.write(string.ljust('Number of Occurrences', 25) + CRT)
fp.write(string.ljust('------', 100))
fp.write(string.ljust('---------------------', 25) + CRT)

#
# select all libraries for given job stream which do not appear within another job stream
#

results = db.sql('select qc1.strain, qc1.numberOfOccurrences ' + \
	   'from QC_MS_InvalidStrain qc1 ' + \
           'where qc1._JobStream_key = %s ' % (jobStreamKey) + \
	   'and not exists (select 1 from QC_MS_InvalidStrain qc2 ' + \
	   'where qc1.strain = qc2.strain ' + \
	   'and qc1._JobStream_key != qc2._JobStream_key) ' + \
	   ' order by qc1.numberOfOccurrences desc, qc1.strain', 'auto')

rows = 0
for r in results:
    fp.write(string.ljust(r['strain'], 100) + \
	     string.ljust(str(r['numberOfOccurrences']), 25) + CRT)
    rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

