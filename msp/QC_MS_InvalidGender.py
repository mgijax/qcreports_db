#!/usr/local/bin/python

'''
#
# Report:
#       This script produces a report of Invalid Genders
#       from QC_MS_InvalidGender.
#
# Usage:
#       QC_MS_InvalidGender.py OutputDir JobKey
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

#
# Main
#

fp = reportlib.init(sys.argv[0],  
		    'Molecular Source Processer - Invalid Genders (Job Stream %s)' % (jobStreamKey), 
		    outputdir = outputDir)

fp.write("  A row in this report represents a Gender that could not be translated to a valid MGI Gender.\n" + \
"  This Gender may need to be added to the Gender bad name/good name list.\n" + 2*CRT)

fp.write(string.ljust('Gender', 100))
fp.write(string.ljust('Number of Occurrences', 25) + CRT)
fp.write(string.ljust('------', 55))
fp.write(string.ljust('---------------------', 25) + CRT)

#
# select all libraries for given job stream which do not appear within another job stream
#

results = db.sql('select qc1.gender, qc1.numberOfOccurrences ' + \
	   'from QC_MS_InvalidGender qc1 ' + \
           'where qc1._JobStream_key = %s ' % (jobStreamKey) + \
	   'and not exists (select 1 from QC_MS_InvalidGender qc2 ' + \
	   'where qc1.gender = qc2.gender ' + \
	   'and qc1._JobStream_key != qc2._JobStream_key) ' + \
	   ' order by qc1.numberOfOccurrences desc, qc1.gender', 'auto')

rows = 0
for r in results:
    fp.write(string.ljust(r['gender'], 100) + \
	     string.ljust(str(r['numberOfOccurrences']), 25) + CRT)
    rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

