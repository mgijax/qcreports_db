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
import re
import db
import mgi_utils
import reportlib

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])
fp.write('Invalid "Inferred From" Values in GO Annotations (MGI, GO)' + 2 * reportlib.CRT)
rows = 0

# use for Mol Segs...quicker than mgiLookup method due to number of Mol Segs

findID = 'select _Object_key from ACC_Accession where accID = "%s"'

# read in all MGI accession ids for Markers (2), Alleles (11)
# read in all GO ids (13)
# this is the list of valid accession ids

mgiLookup = []
results = db.sql('select a.accID from ACC_Accession a where a._MGIType_key in (2, 11) and a.prefixPart = "MGI:"', 'auto')
for r in results:
    mgiLookup.append(r['accID'])
results = db.sql('select a.accID from ACC_Accession a where a._MGIType_key = 13 and a.prefixPart in ("GO:")', 'auto')
for r in results:
    mgiLookup.append(r['accID'])

# read in all annotations that contains MGD or GO

db.sql('''
	select a._Term_key, a._Object_key, e.inferredFrom, evidenceCode = t.abbreviation 
	into #annotations 
	from VOC_Annot a, VOC_Evidence e, VOC_Term t 
	where a._AnnotType_key = 1000 
	and a._Annot_key = e._Annot_key 
	and e.inferredFrom != null 
	and (e.inferredFrom like '%MGI%' or e.inferredFrom like '%GO%')
	and e._EvidenceTerm_key = t._Term_key
	''', None)
db.sql('create nonclustered index idx1 on #annotations(_Term_key)', None)
db.sql('create nonclustered index idx2 on #annotations(_Object_key)', None)
db.sql('create nonclustered index idx3 on #annotations(inferredFrom)', None)

# retrieve GO acc ID, marker symbol

results = db.sql('''
	select e.inferredFrom, a.accID, m.symbol, e.evidenceCode 
	from #annotations e, ACC_Accession a, MRK_Marker m 
	where e._Term_key = a._Object_key 
	and a._MGIType_key = 13 
	and a.preferred = 1 
	and e._Object_key = m._Marker_key 
	order by e.inferredFrom
	''', 'auto')

for r in results:
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
	id = re.sub('"', '', id)
	id.upper()

	if string.find(id, 'MGI:') >= 0 or string.find(id, 'GO:') >= 0:
	    if id not in mgiLookup:
		fp.write(id + reportlib.TAB + \
			 r['accID'] + reportlib.TAB + \
			 r['evidenceCode'] + reportlib.TAB + \
			 r['symbol'] + reportlib.CRT)
		rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))
reportlib.finish_nonps(fp)

