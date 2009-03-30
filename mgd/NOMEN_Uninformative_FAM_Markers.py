#!/usr/local/bin/python

'''
#
# TR 9452
#
# Report:
# Please create a new report for Nomen which lists human FAM genes whose mouse 
# orthologs don't have informative nomenclature e.g. Rikens, Vega symbols, SeqIDs 
# as symbols.  The report could be called "FAM orthologs with uninformative 
# nomenclature".
#
# I would like the first column to list the FAM symbol used by HGNC and the 
# second column to contain its orthologous mouse symbol.
#
# Usage:
#       NOMEN_Uninformative_FAM_Markers.py
#
# Notes:
#
# History:
#
# mhall	03/28/2008
#	- TR 9452 - created
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

fp = reportlib.init(sys.argv[0], 'FAM orthologs with uninformative nomenclature', os.environ['QCOUTPUTDIR'])


cmds = []


# Get the total list of all HGNC Supplied Markers, and thier Mouse Orthologs

cmds.append('select distinct hm.symbol as "hsymbol", ' + \
	'mm.symbol as "msymbol", mm._Marker_key as "mkey" ' + \
    	'into #hgncmarkers ' + \
    	'from MRK_Homology_Cache mh, MRK_Homology_Cache hh, ' + \
    	'MRK_Marker mm, MRK_Marker hm, acc_accession a ' + \
    	'where mh._Class_key = hh._Class_key ' + \
    	'and hm._Marker_key = hh._Marker_key ' + \
    	'and hm.symbol like "FAM%" ' + \
    	'and mh._Marker_key = mm._Marker_key ' + \
    	'and mh._Organism_key = 1 ' + \
    	'and hh._Organism_key = 2 ' + \
    	'and a._Object_key = hm._Marker_key ' + \
    	'and a._MGIType_key = 2 ' + \
    	'and a._LogicalDB_key = 64 ')

# Now, get all the uninformative ones from this list.

cmds.append('select distinct hsymbol as "Human Symbol", msymbol as "Mouse Symbol" ' + \
	'from #hgncmarkers ' + \
	'where msymbol like "%rik%" ' + \
	'union ' + \
	'select distinct hsymbol as "Human Symbol", msymbol as "Mouse Symbol" ' + \
	'from #hgncmarkers ' + \
	'where msymbol like "eg%" ' + \
	'union ' + \
	'select distinct hsymbol as "Human Symbol", msymbol as "Mouse Symbol" ' + \
	'from #hgncmarkers h, acc_accession a ' + \
	'where msymbol = accID ' + \
	'union ' + \
	'select distinct hsymbol as "Human Symbol", msymbol as "Mouse Symbol" ' + \
	'from #hgncmarkers h, mrk_marker m ' + \
	'where h.mkey = m._Marker_key and m.name like "%dna segment%" ' + \
	'union ' + \
	'select distinct hsymbol as "Human Symbol", msymbol as "Mouse Symbol" ' + \
	'from #hgncmarkers h, mrk_marker m ' + \
	'where h.mkey = m._Marker_key and m.name like "%gene model%" ')


results = db.sql(cmds,'auto')

fp.write(string.ljust('Human Symbol', 40) + '  ' + \
         string.ljust('Mouse Symbol', 35) + CRT)
fp.write('-'*40 + '  ' + '-'*35 + CRT)

for r in results[1]:
    fp.write(string.ljust(r['Human Symbol'], 40) + '  ' + \
             string.ljust(r['Mouse Symbol'], 35) + CRT)

fp.write(CRT + 'Row count: ' + str(len(results[1])) + CRT*3)

reportlib.finish_nonps(fp)

