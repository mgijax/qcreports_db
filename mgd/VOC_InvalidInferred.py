#!/usr/local/bin/python

'''
#
# VOC_InvalidInferred.py 10/17/2003
#
# Report:
#	TR 5311
#
#       Tab-delimited file
#       Annotation Evidence Inferred From Accession IDs
#	which are invalid.
#
# Usage:
#       VOC_InvalidInferred.py
#
# Used by:
#       Annotation Editors
#
# Notes:
#
# History:
#
# lec	11/14/2003
#	- new
#
'''
 
import sys
import os
import string
import regsub
import db
import mgi_utils
import reportlib

#
# Main
#

db.useOneConnection(1)

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCREPORTOUTPUTDIR'])
fp.write('Invalid "Inferred From" Values in GO Annotations (MGI and InterPro only)' + 2 * reportlib.CRT)
rows = 0

# use for Mol Segs...quicker than mgiLookup method due to number of Mol Segs

findID = 'select _Object_key from ACC_Accession where accID = "%s"'

mgiLookup = []
cmds = []

# read in all MGI accession ids for Markers (2), Alleles (11)
# read in all InterPro ids (13)

cmds.append('select a.accID from ACC_Accession a where a._MGIType_key in (2, 11) and a.prefixPart = "MGI:" ')
cmds.append('select a.accID from ACC_Accession a where a._MGIType_key = 13 and a.prefixPart = "IPR"')

# read in all annotations w/ non-null inferred from value

cmds.append('select a._Term_key, a._Object_key, e.inferredFrom ' + \
	'into #annotations ' + \
	'from VOC_Annot a, VOC_Evidence e ' + \
	'where a._AnnotType_key = 1000 ' + \
	'and a._Annot_key = e._Annot_key ' + \
	'and e.inferredFrom != null ')

cmds.append('create nonclustered index idx1 on #annotations(_Term_key)')
cmds.append('create nonclustered index idx2 on #annotations(_Object_key)')
cmds.append('create nonclustered index idx3 on #annotations(inferredFrom)')

# retrieve GO acc ID, marker symbol

cmds.append('select e.inferredFrom, a.accID, m.symbol ' + \
'from #annotations e, ACC_Accession a, MRK_Marker m ' + \
'where e._Term_key = a._Object_key ' + \
'and a._MGIType_key = 13 ' + \
'and a.preferred = 1 ' + \
'and e._Object_key = m._Marker_key ' + \
'order by e.inferredFrom')

results = db.sql(cmds, 'auto')

for r in results[0]:
    mgiLookup.append(r['accID'])
for r in results[1]:
    mgiLookup.append(r['accID'])

for r in results[-1]:
    ids = r['inferredFrom']

    if string.find(ids, ', ') >= 0:
	delimiter = ', '
    elif string.find(ids, ',') >= 0:
	delimiter = ','
    elif string.find(ids, '; ') >= 0:
	delimiter = '; '
    elif string.find(ids, '|') >= 0:
	delimiter = '|'
    else:
	delimiter = ''

    if len(delimiter) > 0:
        idList = string.split(ids, delimiter)
    else:
	idList = [ids]

    for id in idList:
	id = regsub.gsub('"', '', id)

	if string.find(id, 'MGI:') >= 0:
	    if id not in mgiLookup:
		# it's not in our set, so query the database directly
		results = db.sql(findID % (id), 'auto')
		if len(results) == 0:
		    	fp.write(id + reportlib.TAB + r['accID'] + reportlib.TAB + r['symbol'] + reportlib.CRT)
			rows = rows + 1

	if string.find(id, 'INTERPRO:') >= 0:
	    [prefixPart, idPart] = string.split(id, 'INTERPRO:')
	    if idPart not in mgiLookup:
		fp.write(id + reportlib.TAB + r['accID'] + reportlib.TAB + r['symbol'] + reportlib.CRT)
		rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))
db.useOneConnection(0)
reportlib.finish_nonps(fp)

