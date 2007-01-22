#!/usr/local/bin/python

'''
#
# Report:
#
#	Ensembl Gene Models with no Marker Association
#
#       Produce a tab-delimited report with the following output fields:
#
#       Ensembl Gene Model ID
#
# Usage:
#       MRK_NoENSEMBL.py
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

fp.write('#\n')
fp.write('# Ensembl Gene Models with no Marker Association\n')
fp.write('#\n')

results = db.sql('select a.accID ' + \
      'from ACC_Accession a ' + \
      'where a._MGIType_key = 19 and ' + \
      'a._LogicalDB_key = 60 and ' + \
      'not exists (select 1 from SEQ_Marker_Cache s where a._Object_key = s._Sequence_key) ' + \
	'order by a.accID', 'auto')

for r in results:
    fp.write(r['accID'] + CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))

reportlib.finish_nonps(fp)
