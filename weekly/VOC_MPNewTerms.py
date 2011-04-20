#!/usr/local/bin/python

'''
#
# MP_NewTerms.py
#
# Report:
#       Weekly MP New Term report
#
# Usage:
#      MP_NewTerms.rpt
#
# Notes:
#	- all reports use mgireport directory for output file
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- use proper case for all table and column names e.g. 
#         use MRK_Marker not mrk_marker
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
# 	- sc 4/7/2011 new
#
'''
 
import sys 
import os
import string
import db
import reportlib
import mgi_utils

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE
#reportlib.column_width = 150

#
# Main
#

currentDate = mgi_utils.date('%m/%d/%Y')
fromDate = db.sql('select convert(char(10), dateadd(day, -7, "%s"), 101) ' % (currentDate), 'auto')[0]['']

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

db.sql('''select a.accid, t.term , t._Term_key, t.creation_date
into #triage
from VOC_Term t, ACC_Accession a
where t.creation_date between "%s" and "%s"
and t._Term_key = a._Object_key
and a._LogicalDB_key = 34
and a._MGIType_key = 13''' % (fromDate, currentDate), None)

db.sql('''create index idx1 on #triage(_Term_key)''', None)

results = db.sql('''select distinct t.accid, 
    t.term, s.synonym
    from #triage t, MGI_Synonym s
    where t._Term_key = s._Object_key
    and s._MGIType_key = 13
    union
    select distinct t.accid,
    t.term, synonym = null
    from #triage t where not exists (
	select 1 from MGI_Synonym s
	where t._Term_key = s._Object_key
	and s._MGIType_key = 13)
    order by t.term''', 'auto')

# MP ID:list of results
rDict = {}
for r in results:
    accid = (r['accid'])
    if not rDict.has_key(accid):
	rDict[accid] = []
    rDict[accid].append(r)

mpIds = rDict.keys()
mpIds.sort()

fp.write( 'MP Terms Added From %s to %s%s%s' % (fromDate, currentDate, CRT, CRT) )

fp.write(string.ljust('MP ID', 15))
fp.write(string.ljust('MP Term', 75))
fp.write(string.ljust('Synonyms', 50) + CRT)
fp.write(string.ljust('-----',  15))
fp.write(string.ljust('-------',  75))
fp.write(string.ljust('--------',  50) + CRT)
for id in mpIds:
    resultList = rDict[id]
    term = resultList[0]['term']
    synonymList = []
    for r in resultList:
        s = r['synonym']
	if s != None:
	    synonymList.append(r['synonym'])
    synonyms = string.join(synonymList, ', ')
    fp.write(string.ljust(id, 15) )
    fp.write(SPACE)
    fp.write(string.ljust(term, 75) )
    fp.write(SPACE)
    fp.write(string.ljust(synonyms, 50) )
    fp.write(CRT)

fp.write('%sNumber of new terms this week: %s' % (CRT, len(mpIds)) )

reportlib.finish_nonps(fp)	# non-postscript file

