#!/usr/local/bin/python

'''
#
# VOC_InvalidProperties.py 10/17/2003
#
# Report:
#       Tab-delimited file
#	Annotation Properties that contain invalid terms
#
# Usage:
#       VOC_InvalidProperties.py
#
# Used by:
#       Annotation Editors
#
# Notes:
#
# History:
#
#
'''
 
import sys
import os
import string
import mgi_utils
import reportlib
import db

#db.setTrace()
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])
fp.write('\nInvalid "Properties" Values in GO Annotations' + 2 * reportlib.CRT)
rows = 0

# read in all term ids (13) of interest
# this is the list of valid accession ids

mgiLookup = []
results = db.sql('''
select a.accID from ACC_Accession a, VOC_Term t
where a._MGIType_key = 13 
and a._Object_key = t._Term_key
and t.isObsolete = 0
and t._Vocab_key in (102)
order by a.accID
''', 'auto')
for r in results:
    mgiLookup.append(r['accID'])

# read in all annotations that contains terms of interest

db.sql('''
	select distinct p.value, aa.accID, m.symbol
	into temporary table annotations 
	from VOC_Annot a, VOC_Evidence e, VOC_Evidence_Property p,
		ACC_Accession aa, MRK_Marker m
	where a._AnnotType_key = 1000 
	and a._Annot_key = e._Annot_key 
	and e._AnnotEvidence_key = p._AnnotEvidence_key
	and p.value is not null 
	and p.value like '%CL:%'
        and a._Term_key = aa._Object_key 
        and aa._MGIType_key = 13  
        and aa.preferred = 1 
        and a._Object_key = m._Marker_key 
	order by p.value
	''', None)

results = db.sql('select * from annotations', 'auto')

for r in results:
    ids = r['value']
    ids = ids.replace('%', '|')
    ids = ids.replace('!', '|')
    ids = ids.replace(';', '|')
    ids = ids.replace(',', '|')
    ids = ids.replace('(', '|')
    ids = ids.replace(')', '|')
    ids = ids.replace(' ', '')
    ids = ids.upper()
    delimiter = '|'
    idList = string.split(ids, delimiter)

    for id in idList:
	if string.find(id, 'CL:') >= 0:
		if id not in mgiLookup:
        		fp.write(r['accID'] + reportlib.TAB + \
				r['symbol'] + reportlib.TAB + \
        			r['value'] + reportlib.CRT)
			rows = rows + 1 

fp.write('\n(%d rows affected)\n' % (rows))
reportlib.finish_nonps(fp)

