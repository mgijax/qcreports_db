#!/usr/local/bin/python

#
# Check MLC Image Index file on Production
#

import sys
import os
import string
import db
import reportlib

#
# Main Routine
#

inputFile = open('/usr/local/mgi/wi/prod/www/images/mlc/index', 'r')
fp = reportlib.init(sys.argv[0], 'MLC Image Index File Entries Which Contain Withdrawn Symbols', os.environ['QCREPORTOUTPUTDIR'])
fp.write(string.ljust('MGD Withdrawn Symbol', 25) + reportlib.TAB + 'Image Entry\n\n')

for line in inputFile.readlines():
	tokens = string.splitfields(string.strip(line), '|')

	cmd = 'select _Marker_key, _Marker_Status_key, symbol from MRK_Marker ' + \
	      'where symbol = "' + tokens[0] + '"'
	results = db.sql(cmd, 'auto')

	for r in results:
		if r['symbol'] == tokens[0] and r['_Marker_Status_key'] == 2:
			fp.write(string.ljust(r['symbol'], 25) + reportlib.TAB + \
				 tokens[1] + "|" + \
				 tokens[2] + "|" + \
				 tokens[3] + reportlib.CRT)

inputFile.close()
reportlib.trailer(fp)
reportlib.finish_nonps(fp)

