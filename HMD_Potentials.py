#!/usr/local/bin/python

#
# TR 390
#
# Process download file from GDB 'Gene.medlineid.tab'.
#
# This file contains GDB symbols and their citations.  If the citation has a
# medline ui, then use this value to search for the reference in MGD.  If the
# citation does not have a medline ui, then ignore the citation.
#
# If the reference can be found in MGD and there is no human homology record in MGD
# for the GDB symbol, then print out the mouse symbol, human symbol, etc.
#
# This will reveal potential mouse/human homologies.
#

import sys
import os 
import db
import string
import regex
import reportlib

inFile = open('%s/Gene.medlineid.tab' % (os.environ['QCREPORTOUTPUTDIR']), 'r')

reportName = 'HMD_Potentials'
fp = reportlib.init(reportName, 'GDB citations which match MGD w/ no Human Homology', os.environ['QCREPORTOUTPUTDIR'])
fp.write('%-10s %-50s %-20s %-15s %-20s\n\n' % ('J#', 'Citation', 'Mouse Symbol', 'Human Symbol', 'GDB Acc ID'))

cmd = 'create table tempdb..gdbmedline (' + \
	'accid varchar(30) not null,' + \
	'symbol varchar(30) not null,' + \
	'medline varchar(30) not null)\n'
db.sql(cmd, None)

for line in inFile.readlines():

	if string.find(line, 'GDB') >= 0:
		tokens = string.splitfields(string.strip(line), '\t')

		accid = tokens[0]
		symbol = tokens[1]

		if len(tokens) < 3:
			continue

		refs = string.splitfields(tokens[2], ';')

		for r in refs:
			if regex.match('[0-9]', r) > 0:
				medline = r

				cmd = 'insert into tempdb..gdbmedline ' + \
					'values ("%s", "%s", "%s")' % (accid, symbol, medline)
				db.sql(cmd, None)

inFile.close()

cmd = 'create index index_accid on tempdb..gdbmedline (accid)'
db.sql(cmd, None)

cmd = 'create index index_symbol on tempdb..gdbmedline (symbol)'
db.sql(cmd, None)

cmd = 'create index index_medline on tempdb..gdbmedline (medline)'
db.sql(cmd, None)

cmd = 'select r.jnumID, r.short_citation, m.symbol, gdbsymbol = g.symbol, g.accid ' + \
      'from tempdb..gdbmedline g, BIB_All_View r, BIB_Acc_View a, MRK_Reference mr, MRK_Marker m ' + \
      'where a.accid = g.medline ' + \
      ' and a._Object_key = r._Refs_key ' + \
      ' and a._Object_key = mr._Refs_key ' + \
      ' and mr._Marker_key = m._Marker_key ' + \
      ' and m._Species_key = 1 ' + \
      ' and m._Marker_Type_key != 2 ' + \
      ' and m.symbol = g.symbol ' + \
      ' and not exists ' + \
      '(select 1 from HMD_Homology_Marker h1, ' + \
      'HMD_Homology_Marker h2, MRK_Marker m2 ' + \
      ' where m._Marker_key = h1._Marker_key and ' + \
      ' h1._Homology_key = h2._Homology_key and ' + \
      ' h2._Marker_key = m2._Marker_key and ' + \
      ' m2._Species_key = 2)'

results = db.sql(cmd, 'auto')
for r in results:
	fp.write('%-10s %-50s %-20s %-15s %-20s\n'
		% (r['jnumID'], r['short_citation'],
		   r['symbol'], r['gdbsymbol'], r['accid']))

cmd = 'drop table tempdb..gdbmedline'
db.sql(cmd, None)

reportlib.trailer(fp)
reportlib.finish_nonps(fp)

