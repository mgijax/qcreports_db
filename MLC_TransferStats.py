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
# Generated from:
#       Editing Interface, MLC Report form
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
import mgdlib
import reportlib

CRT = reportlib.CRT

### MAIN ####

fp = reportlib.init('MLC_TransferStats', 'MLC Transfer Statistics Report', os.environ['QCREPORTOUTPUTDIR'])

cmd = 'select m.symbol ' + \
      'from MLC_Text_edit t, MRK_Marker m ' + \
      'where t._Marker_key = m._Marker_key ' + \
      'and not exists (select t2._Marker_key ' + \
                       'from MLC_Text t2 ' + \
                       'where t2._Marker_key = t._Marker_key)'

mkadds = mgdlib.sql(cmd, 'auto')

cmd = 'select m.symbol ' + \
      'from MLC_Text t, MRK_Marker m ' + \
      'where t._Marker_key = m._Marker_key ' + \
      'and not exists (select t2._Marker_key ' + \
                       'from MLC_Text_edit t2 ' + \
                       'where t2._Marker_key = t._Marker_key)'
mkdeletes = mgdlib.sql(cmd, 'auto')

cmd = 'select m.symbol ' + \
      'from MLC_Text_edit te, MRK_Marker m, MLC_Text t ' + \
      'where te._Marker_key = m._Marker_key ' + \
      'and te._Marker_key = t._Marker_key ' + \
      'and te.modification_date > ' + \
      '    t.modification_date' 
mkupdates = mgdlib.sql(cmd, 'auto')

indent=2 

class Paragraph:
	def __init__(self, title, results):
		'''
		# title is the subheading to be printed for this paragraph,
		# results is the result of mgdlib.sql(cmd,'auto') 
		'''
		self.title = title
		self.results = results
	def getTitle(self):
		return self.title
	def getResults(self):
		return self.results


addsymbols    = []
for row in mkadds:
	addsymbols.append(row['symbol'])
addsymbols.sort()

# updates are detected by modification date.  Adds will show up
# here as well, so we will exclude them.

updatesymbols = []
for row in mkupdates:
	symbol = row['symbol']
	try: 
		addsymbols.index(symbol)
	except:
		updatesymbols.append(symbol)
updatesymbols.sort()

deletesymbols = []
for row in mkdeletes:
	deletesymbols.append(row['symbol'])
deletesymbols.sort()

paragraphs = [Paragraph('MLC Adds needing transfer to Production:', 
                         addsymbols),
              Paragraph('MLC Updates needing transfer to Production:', 
                         updatesymbols),
              Paragraph('MLC Deletes needing transfer to Production:', 
                         deletesymbols)]

for paragraph in paragraphs:
	fp.write(paragraph.getTitle())
	fp.write('(' + `len(paragraph.getResults())` + ')' + 2*CRT)
	fp.write(15*'-' + CRT)

	for symbol in paragraph.getResults():
		fp.write(indent*' ' + symbol + CRT) 

	fp.write(2*CRT)

reportlib.finish_nonps(fp)
