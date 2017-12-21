#!/usr/local/bin/python

'''
#
# TR12250/Lit Triage
#
# Report:
#
# Usage:
#       WF_GXD_secondary.py
#
#	Group = GXD
#	Status = Not Routed
#	Is Discared = false
#	Jnum ID is not null
# 	Tag *not* in ('GXD:cms', 'GXD:jf', 'GXD:th', 'GXD:jx', 'GXD:ijm')
#
#	compare embryo_set with ignore_set
#	ignore_set = references where ignore set exists in extracted text
#	embryo_set = references where "%embryo%" exists in extracted text
#
# J:249490 : has 'human embryonic stem' which gets counted for all 3:
#	human embryonic stem
#	human embryonic
#	embryonic stem
#
# History:
#
# 12/15/2017
#	- TR12717/GXD secondary screening
#
'''
 
import sys 
import os 
import re
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# find each searcht term in extractedText field
# save results in ignoreLookup
#
def findExtractedText(extractedText):

    ignoreLookup = []
    ignoreCount = 0

    for s in ignoreSearchTerms:

	# count each instance of search term
        counter = extractedText.count(s)

	if counter > 0:

	    #
	    # this will be counted 3 times, but only count 1
	    # human embryonic stem, human embryonic, embryonic stem
	    #
	    if s == 'human embryonic stem':
	        counter = counter - 2

	    ignoreCount += counter

	    if s not in ignoreLookup:
	        ignoreLookup.append(s)

    #print ignoreLookup, ignoreCount
    return ignoreLookup, ignoreCount

#
# Main
#

#
# ignored search terms 
#
ignoreSearchTerms = []
results = db.sql('select term from VOC_Term where _Vocab_key = 135 order by term', 'auto')
for r in results:
    ignoreSearchTerms.append(r['term'])

#
# references : see rules at top
#
db.sql('''
select r._Refs_key, r.jnumID, 
	lower(regexp_replace(d.extractedtext, E'\n', ' ', 'g')) as extractedText
into temp table refs
from BIB_Citation_Cache r, BIB_Workflow_Status s, BIB_Workflow_Data d
where r.isDiscard = 0
and r.jnumID is not null
and r._Refs_key = s._Refs_key
and s.isCurrent = 1
and s._Group_key = 31576665
and s._Status_key = 31576669
and r._Refs_key = d._Refs_key
and not exists (select 1 from BIB_Workflow_Tag t, VOC_Term v 
         where r._Refs_key = t._Refs_key
         and t._Tag_key = v._Term_key
         and v.term in ('GXD:cms', 'GXD:jf', 'GXD:th', 'GXD:jx', 'GXD:ijm')
         )
''', None)

db.sql('create index idx_refs on refs(_Refs_key)', None)

#results = db.sql('select * from refs', 'auto')
#print results

#
# create ignore_set
#
db.sql('''
select r.*
into temp table ignore_set
from refs r, VOC_Term t
where r.extractedText like '%' || t.term || '%'
and t._Vocab_key = 135
''', None)

db.sql('create index idx_ignore on ignore_set(_Refs_key)', None)

#
# create embryo_set
#
db.sql('''
select r.*
into temp table embryo_set
from refs r
where r.extractedText like '%embryo%'
''', None)

db.sql('create index idx_embryo on embryo_set(_Refs_key)', None)

fp1 = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

fp1.write('\nset of "Lit Triage GXD ignore extracted text" (_vocab_key = 135):\n')
fp1.write('\n'.join(ignoreSearchTerms) + '\n\n')

fp1.write('ignore_set = references where ignore set exists in extracted text\n')
fp1.write('embryo_set = references where "%embryo%" exists in extracted text\n')

#
# embryo_set count of "%embryo%" results 
# use regexp_match() to get counts of each instance of match
#
embryoLookup = {}
results = db.sql('''
select _Refs_key, count(*) as set_count 
from embryo_set, regexp_matches(extractedText, '(embryo)', 'g')
group by _Refs_key
''', 'auto')
for r in results:
    key = r['_Refs_key']
    value = r['set_count']
    if key not in embryoLookup:
        embryoLookup[key] = []
    embryoLookup[key] = value
#print embryoLookup

#
# references in embryo_set and not in ignore_set
#
fp1.write('\nreferences in embryo_set and not in ignore_set : good')
fp1.write('\nreferences in embryo_set and in ignore_set : good\n\n')
count = 0
results = db.sql('''
select distinct s2._Refs_key, s2.jnumID, s2.extractedText
from embryo_set s2
where not exists (select 1 from ignore_set s1 where s2._Refs_key = s1._Refs_key)
order by s2.jnumID
''', 'auto')
for r in results:
    fp1.write(r['jnumID'] + TAB)
    ignoreLookup, ignoreCount = findExtractedText(r['extractedText'])
    fp1.write('|'.join(ignoreLookup) + CRT)
    count +=1

#
# references in embryo_set and in ignore_set 
# where embryo_set count > ignoreCount
#
results = db.sql('''
select distinct s2._Refs_key, s2.jnumID, s2.extractedText
from ignore_set s1, embryo_set s2
where s1._Refs_key = s2._Refs_key
order by s2.jnumID
''', 'auto')
for r in results:
    ignoreLookup, ignoreCount = findExtractedText(r['extractedText'])
    if embryoLookup[r['_Refs_key']] > ignoreCount:
        fp1.write(r['jnumID'] + TAB)
        fp1.write('|'.join(ignoreLookup) + CRT)
	count += 1
fp1.write('\n(%d rows affected)\n' % (count))

#
# references in ignore_set but not in embryo_set
# where embryo_set count == ignoreCount
#
fp1.write('\nreferences in ignore_set and not in embryo_set : bad\n\n')
count = 0
ignoreLookup = []
results = db.sql('''
select distinct s2._Refs_key, s2.jnumID, s2.extractedText
from ignore_set s1, embryo_set s2
where s1._Refs_key = s2._Refs_key
order by s2.jnumID
''', 'auto')
for r in results:
    ignoreLookup, ignoreCount = findExtractedText(r['extractedText'])
    if embryoLookup[r['_Refs_key']] == ignoreCount:
        fp1.write(r['jnumID'] + TAB)
        fp1.write('|'.join(ignoreLookup) + CRT)
	count += 1
fp1.write('\n(%d rows affected)\n' % (count))

reportlib.finish_nonps(fp1)

