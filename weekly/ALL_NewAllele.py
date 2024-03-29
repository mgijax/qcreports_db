
'''
#
# ALL_NewAllele.py
#
# Report:
#       Weekly New Alleles Report
#
# Usage:
#       ALL_NewAllele.py
#
# History:
#
# 08/29/2018	lec
#	- TR12946/add marker names
#
# 10/4/2011	sc
# Alicia has asked for some modifications:
# 1. Add columns for Allele Type and Synonyms.
# 2. Create an archive for the report. 
#	(This may already exist but please add a link to the archive 
#	from the qcreport page.)
#
# 08/25/2011	lec
#	- TR10822
#
'''

import sys 
import os
import mgi_utils
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# Main
#

fromDate = "current_date - interval '7 days'"
toDate = "current_date - interval '1 day'"

synonymDict = {}

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], fileExt = '.' + os.environ['DATE'] + '.rpt', printHeading = None)

results = db.sql('''
        select _Object_key as alleleKey, synonym
        from MGI_Synonym
        where _MGIType_key = 11
        ''', 'auto')
for r in results:
    key = r['alleleKey']
    if key not in synonymDict:
        synonymDict[key] = []
    synonymDict[key].append(r['synonym'])

results = db.sql('''
        (
        select a._Allele_key, a.symbol, 
        substring(a.name,1,60) as name, 
        substring(m.name,1,60) as markerName,
        substring(t1.term,1,15) as status, 
        substring(t2.term, 1, 60) as type,
        ac.accID,
        u.login
        from ALL_Allele a, MRK_Marker m, VOC_Term t1, VOC_Term t2, MGI_Reference_Assoc r, ACC_Accession ac, MGI_User u
        where a._Allele_Status_key = t1._Term_key
        and a._Allele_Type_key = t2._Term_key
        and a.creation_date between %s and %s
        and a._Marker_key = m._Marker_key
        and a._Allele_key = r._Object_key
        and r._MGIType_key = 11
        and r._RefAssocType_key = 1011
        and r._Refs_key = ac._Object_key 
        and ac._MGIType_key = 1
        and ac._LogicalDB_key = 1
        and ac.prefixPart = 'J:'
        and ac.preferred = 1
        and a._modifiedby_key = u._user_key
        union
        select a._Allele_key, a.symbol, 
        substring(a.name,1,60) as name, 
        null,
        substring(t1.term,1,15) as status, 
        substring(t2.term, 1, 60) as type,
        ac.accID,
        u.login
        from ALL_Allele a, VOC_Term t1, VOC_Term t2, MGI_Reference_Assoc r, ACC_Accession ac, MGI_User u
        where a._Allele_Status_key = t1._Term_key
        and a._Allele_Type_key = t2._Term_key
        and a.creation_date between %s and %s
        and a._Marker_key is null
        and a._Allele_key = r._Object_key
        and r._MGIType_key = 11
        and r._RefAssocType_key = 1011
        and r._Refs_key = ac._Object_key 
        and ac._MGIType_key = 1
        and ac._LogicalDB_key = 1
        and ac.prefixPart = 'J:'
        and ac.preferred = 1
        and a._modifiedby_key = u._user_key
        )
        order by symbol
        ''' % (fromDate, toDate, fromDate, toDate), 'auto')

for r in results:
        alleleKey = r['_Allele_key']

        fp.write(mgi_utils.prvalue(r['symbol']) + TAB)
        fp.write(mgi_utils.prvalue(r['name']) + TAB)
        fp.write(mgi_utils.prvalue(r['markerName']) + TAB)

        synonyms = ''
        if alleleKey in synonymDict:
            synonyms = ''.join(synonymDict[alleleKey])
        fp.write(synonyms + TAB)

        fp.write(mgi_utils.prvalue(r['type']) + TAB)
        fp.write(mgi_utils.prvalue(r['status']) + TAB)
        fp.write(mgi_utils.prvalue(r['accID']) + TAB)
        fp.write(mgi_utils.prvalue(r['login']) + CRT)

reportlib.finish_nonps(fp)	# non-postscript file
