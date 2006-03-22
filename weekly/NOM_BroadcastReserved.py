#!/usr/local/bin/python

'''
#
# TR 3958 - Reserved Nomen Markers Broadcast in the last week
#
# Usage:
#       NOM_BroadcastReserved.py
#
# Notes:
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
#
# lec	08/01/2002
#	- created
#
'''
 
import sys 
import os
import regsub
import db
import mgi_utils
import reportlib

#
# Main
#

if len(sys.argv) > 1:
	currentDate = sys.argv[2]
else:
	currentDate = mgi_utils.date('%m/%d/%Y')

fp = reportlib.init(sys.argv[0], printHeading = 0, outputdir = os.environ["QCOUTPUTDIR"])

cmd = 'select n.symbol, bdate = convert(char(10), n.broadcast_date, 101), n.statusNote, a.accID, ' + \
'name = substring(n.name,1,50), n.humanSymbol ' + \
'from NOM_Marker n, ACC_Accession a ' + \
'where n._NomenStatus_key in (5,7) ' + \
'and n.statusNote like "%reserved%" ' + \
'and n.broadcast_date between dateadd(day, -7, "%s") ' % (currentDate) + \
'and dateadd(day, 1, "%s") ' % (currentDate) + \
'and n._Nomen_key = a._Object_key ' + \
'and a._MGIType_key = 21 ' + \
'and a._LogicalDB_key = 1 ' + \
'order by n.broadcast_date, n.symbol'

results = db.sql(cmd, 'auto')

for r in results:

	note = regsub.gsub('\n', ' ' , r['statusNote'])
	fp.write(r['symbol'] + reportlib.TAB + \
		 r['bdate'] + reportlib.TAB + \
		 note + reportlib.TAB + \
		 r['accID'] + reportlib.TAB + \
		 r['name'] + reportlib.TAB + \
		 mgi_utils.prvalue(r['humanSymbol']) + reportlib.CRT)

reportlib.finish_nonps(fp)	# non-postscript file

