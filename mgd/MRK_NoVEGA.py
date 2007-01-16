#!/usr/local/bin/python

'''
#
# Report:
#
#	VEGA Gene Models with no Marker Association
#
#       Produce a tab-delimited report with the following output fields:
#
#       VEGA Gene Model ID
#
# Usage:
#       MRK_NoVEGA.py
#
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

results = db.sql('select a.accID ' + \
      'from ACC_Accession a ' + \
      'where a._MGIType_key = 19 and ' + \
      'a._LogicalDB_key = 85 and ' + \
      'not exists (select 1 from SEQ_Marker_Cache s where a._Object_key = s._Sequence_key) ' + \
	'order by a.accID', 'auto')

for r in results:
    fp.write(r['accID'] + CRT)

reportlib.finish_nonps(fp)
