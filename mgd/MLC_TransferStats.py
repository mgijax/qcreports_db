#!/usr/local/bin/python

'''
#
# MLC_TransferStats.py 08/18/98
#
# Report:
#       Compares the entries in the MLC *_edit tables to their non-edit
#       counterparts (which are viewable on the Production DB, releasable 
#       to that Public DB). Because the MLC editing interface is now 
#       allowing release of only a single add/update/delete at a time, 
#       there is a chance that some records will not be released to 
#       Production due to an editor's error. This report summarizes the status 
#       of the MLC tables, displaying lists of adds/updates/deletes that 
#       have not been transferred from the edit tables to the non-edit tables. 
#
# Usage:
#       MLC_TransferStats.py
#
# Notes:
#
# History:
#	gld	08/18/98
#	- written by gld
#
'''
 
import sys
import os
import string
import db
import reportlib

CRT = reportlib.CRT

def printResults(results, title):

	fp.write('MLC %s needing transfer to Production:(%d)' % (title, len(results)) + CRT)
	fp.write(15*'-' + CRT)

	for r in results:
		fp.write(r['symbol'] + CRT)

	fp.write(2*CRT)

### MAIN ####

fp = reportlib.init('MLC_TransferStats', 'MLC Transfer Statistics Report', os.environ['QCREPORTOUTPUTDIR'])

cmd = 'select m.symbol ' + \
      'from MLC_Text_edit t, MRK_Marker m ' + \
      'where t._Marker_key = m._Marker_key ' + \
      'and not exists (select t2._Marker_key ' + \
                       'from MLC_Text t2 ' + \
                       'where t2._Marker_key = t._Marker_key) ' + \
      'order by m.symbol'

printResults(db.sql(cmd, 'auto'), 'Adds')

cmd = 'select m.symbol ' + \
      'from MLC_Text t, MRK_Marker m ' + \
      'where t._Marker_key = m._Marker_key ' + \
      'and not exists (select t2._Marker_key ' + \
                       'from MLC_Text_edit t2 ' + \
                       'where t2._Marker_key = t._Marker_key) ' + \
      'order by m.symbol'

printResults(db.sql(cmd, 'auto'), 'Updates')

# Updates excluding Adds

cmd = 'select m.symbol ' + \
      'from MLC_Text_edit te, MRK_Marker m, MLC_Text t ' + \
      'where te._Marker_key = m._Marker_key ' + \
      'and te._Marker_key = t._Marker_key ' + \
      'and te.creation_date != te.modification_date ' + \
      'and te.modification_date > t.modification_date ' + \
      'order by m.symbol'

printResults(db.sql(cmd, 'auto'), 'Deletes')

reportlib.trailer(fp)
reportlib.finish_nonps(fp)
