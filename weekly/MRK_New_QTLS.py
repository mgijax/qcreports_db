#!/usr/local/bin/python

'''
#
# TR 9452
#
# Report:
# I would like to generate a weekly work report of new QTLs entered into MGD 
# (list of QTL symbols and MGI acession numbers).
#
# Usage:
#       MRK_New_QTLS.py
#
# Notes:
#
# History:
#
# mhall	03/30/2008
#	- TR 9555 - created
#
#
'''
 
import sys 
import os 
import string
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fp = reportlib.init(sys.argv[0], 'New QTL Markers in the previous week', os.environ['QCOUTPUTDIR'])


cmds = []


# Get the list of new QTL Markers from the prior week.

cmds.append('select m.symbol, a.accID ' + \
	'from MRK_Marker m, acc_accession a ' + \
	'where m._Marker_Type_key = 6 and m.creation_date > dateadd(wk, -1, getDate()) ' + \
	'and m._Marker_key = a._Object_key and a._MGIType_key = 2 and a.accID like "MGI:%" ' + \
	'and a.preferred = 1 and m._Marker_Status_key in (1, 3)')

results = db.sql(cmds,'auto')

fp.write(string.ljust('Marker Symbol', 40) + '  ' + \
         string.ljust('MGIID', 35) + CRT)
fp.write('-'*40 + '  ' + '-'*35 + CRT)

for r in results[0]:
    fp.write(string.ljust(r['symbol'], 40) + '  ' + \
             string.ljust(r['accID'], 35) + CRT)

fp.write(CRT + 'Row count: ' + str(len(results[0])) + CRT*3)

reportlib.finish_nonps(fp)

