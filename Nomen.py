#!/usr/local/bin/python

'''
#
# Nomen.py 08/18/1999
#
# Report:
#	Basic Nomen info
#
# Usage:
#       Nomen.py
#
# Generated from:
#       Editing Interface Nomenclature Form
#
# Notes:
#
# History:
#
# lec	08/18/1999
#	- created
#
'''
 
import sys
import string
import os
import mgdlib
import reportlib

CRT = reportlib.CRT
TAB = reportlib.TAB
PAGE = reportlib.PAGE
fp = None

if os.environ.has_key('NOMEN'):
	nomen = os.environ['NOMEN']
else:
	nomen = 'nomen'

nomenFrom = 'from ' + nomen + '..'

cmd = sys.argv[1]

results = mgdlib.sql(cmd, 'auto')

for r in results:

	if fp is None:  
		reportName = 'Nomen.%s.rpt' % r['approvedSymbol']
		fp = reportlib.init(reportName, 'Nomenclature Record', os.environ['QCREPORTOUTPUTDIR'])

	dcmd = 'select *, ' + \
	       'bdate = convert(char(25), broadcast_date), ' + \
	       'cdate = convert(char(25), creation_date), ' + \
	       'mdate = convert(char(25), modification_date) ' + \
	       nomenFrom + 'MRK_Nomen_View where _Nomen_key = %d' % (r['_Nomen_key'])
	details = mgdlib.sql(dcmd, 'auto')

	for d in details:

		fp.write("Event             :  " + mgdlib.prvalue(d['event']) + CRT)
		fp.write("Status            :  "+ mgdlib.prvalue(d['status']) + CRT)
		fp.write("Marker Type       :  " + mgdlib.prvalue(d['markerType']) + CRT)
		fp.write("Chromosome        :  " + mgdlib.prvalue(d['chromosome']) + CRT)
		fp.write("Proposed Symbol   :  " + mgdlib.prvalue(d['proposedSymbol']) + CRT)
		fp.write("Approved Symbol   :  " + mgdlib.prvalue(d['approvedSymbol']) + CRT)
		fp.write("Submitted By      :  " + mgdlib.prvalue(d['userName']) + CRT)
		fp.write("Broadcast Date    :  " + mgdlib.prvalue(d['bdate']) + CRT)
		fp.write("Creation Date     :  " + mgdlib.prvalue(d['cdate']) + CRT)
		fp.write("Modification Date :  " + mgdlib.prvalue(d['mdate']) + CRT)
		fp.write("Human Symbol      :  " + mgdlib.prvalue(d['humanSymbol']) + 2*CRT)
		fp.write("Proposed Name     :  " + mgdlib.prvalue(d['proposedName']) + CRT)
		fp.write("Approved Name     :  " + mgdlib.prvalue(d['approvedName']) + 2*CRT)

		#
		# Other Names
		#

		fp.write("Other Names:" + CRT)
		ocmd = 'select name, isAuthor ' + nomenFrom + 'MRK_Nomen_Other ' + \
			'where _Nomen_key = %d order by isAuthor desc' % (r['_Nomen_key'])
		others = mgdlib.sql(ocmd, 'auto')

		for o in others:
			fp.write(TAB + mgdlib.prvalue(o['name']))
			if o['isAuthor'] == 1:
				fp.write("  (Author)")
			fp.write(CRT)

		fp.write(CRT)

		#
		# References
		#

		fp.write("References:" + CRT)
		rcmd = 'select jnumID, isPrimary ' + nomenFrom + 'MRK_Nomen_Reference_View ' + \
			'where _Nomen_key = %d order by isPrimary desc' % (r['_Nomen_key'])
		refs = mgdlib.sql(rcmd, 'auto')

		for rf in refs:
			fp.write(TAB + mgdlib.prvalue(rf['jnumID']))
			if rf['isPrimary'] == 1:
				fp.write("  (Primary)")
			fp.write(CRT)

		fp.write(CRT)

		#
		# Gene Family
		#

		fp.write("Gene Family:" + CRT)
		gcmd = 'select name ' + nomenFrom + 'MRK_Nomen_GeneFamily_View ' + \
			'where _Nomen_key = %d' % (r['_Nomen_key'])
		gfam = mgdlib.sql(gcmd, 'auto')

		for g in gfam:
			fp.write(TAB + mgdlib.prvalue(g['name']) + CRT)

		fp.write(CRT)

		#
		# Accession Numbers
		#

		fp.write("Accession Numbers:" + CRT)
		acmd = 'select accID, LogicalDB ' + nomenFrom + 'MRK_Nomen_AccNoRef_View ' + \
			'where _Object_key = %d' % (r['_Nomen_key'])
		accs = mgdlib.sql(acmd, 'auto')

		for a in accs:
			fp.write(TAB + mgdlib.prvalue(a['LogicalDB']))
			fp.write(TAB + mgdlib.prvalue(a['accID']) + CRT)

		acmd = 'select accID, jnum, LogicalDB ' + nomenFrom + 'MRK_Nomen_AccRef_View ' + \
			'where _Object_key = %d' % (r['_Nomen_key'])
		accs = mgdlib.sql(acmd, 'auto')

		for a in accs:
			fp.write(TAB + mgdlib.prvalue(a['LogicalDB']))
			fp.write(TAB + mgdlib.prvalue(a['accID']) + TAB + 'J:%d' % a['jnum'] + CRT)

		fp.write(CRT)

		fp.write("Nomenclature Assistant Notes:" + CRT)
		fp.write(mgdlib.prvalue(d['statusNote']) + CRT)

		fp.write("Editor's Notes:" + 2*CRT)
		ncmd = 'select note ' + nomenFrom + 'MRK_Nomen_EditorNotes_View ' + \
			'where _Nomen_key = %d order by sequenceNum' % (r['_Nomen_key'])
		notes = mgdlib.sql(ncmd, 'auto')

		for n in notes:
			fp.write(mgdlib.prvalue(n['note']) + CRT)

		fp.write(CRT)

		fp.write("Nomenclature Coordinator Notes:" + 2*CRT)
		ncmd = 'select note ' + nomenFrom + 'MRK_Nomen_CoordNotes_View ' + \
			'where _Nomen_key = %d order by sequenceNum' % (r['_Nomen_key'])
		notes = mgdlib.sql(ncmd, 'auto')

		for n in notes:
			fp.write(mgdlib.prvalue(n['note']) + CRT)

		fp.write(CRT)
		fp.write(PAGE)

reportlib.finish_nonps(fp)

