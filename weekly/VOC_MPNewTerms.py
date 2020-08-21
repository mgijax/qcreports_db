
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
#
# lec   10/23/2014
#       - TR11750/postres complient
#
# lec   10/22/2014
#       - TR11750/postres complient
#
# 	- sc 4/7/2011 new
#
'''
 
import sys 
import os
import string
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fromDate = "current_date - interval '7 days'"
toDate = "current_date"

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

db.sql('''
        select a.accid, t.term , t._Term_key, t.creation_date
        into temporary table triage
        from VOC_Term t, ACC_Accession a
        where t.creation_date between %s and %s
        and t._Term_key = a._Object_key
        and a._LogicalDB_key = 34
        and a._MGIType_key = 13
        ''' % (fromDate, toDate), None)

db.sql('''create index idx1 on triage(_Term_key)''', None)

results = db.sql('''
        (
        select distinct t.accid, t.term, s.synonym
        from triage t, MGI_Synonym s
        where t._Term_key = s._Object_key
        and s._MGIType_key = 13
        union
        select distinct t.accid, t.term, null
        from triage t where not exists (select 1 from MGI_Synonym s
                where t._Term_key = s._Object_key and s._MGIType_key = 13)
        )
        order by term
        ''', 'auto')

# MP ID:list of results
rDict = {}
for r in results:
    accid = (r['accid'])
    if accid not in rDict:
        rDict[accid] = []
    rDict[accid].append(r)

mpIds = list(rDict.keys())
mpIds.sort()

fp.write( 'MP Terms Added From %s to %s%s%s' % (fromDate, toDate, CRT, CRT) )

fp.write(str.ljust('MP ID', 15))
fp.write(str.ljust('MP Term', 75))
fp.write(str.ljust('Synonyms', 50) + CRT)
fp.write(str.ljust('-----',  15))
fp.write(str.ljust('-------',  75))
fp.write(str.ljust('--------',  50) + CRT)
for id in mpIds:
    resultList = rDict[id]
    term = resultList[0]['term']
    synonymList = []
    for r in resultList:
        s = r['synonym']
        if s != None:
            synonymList.append(r['synonym'])
    synonyms =  ', '.join(synonymList)
    fp.write(str.ljust(id, 15) )
    fp.write(SPACE)
    fp.write(str.ljust(term, 75) )
    fp.write(SPACE)
    fp.write(str.ljust(synonyms, 50) )
    fp.write(CRT)

fp.write('%sNumber of new terms this week: %s' % (CRT, len(mpIds)) )

reportlib.finish_nonps(fp)	# non-postscript file
