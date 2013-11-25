#!/usr/local/bin/python

'''
#
# Report:
    Steve Rockwood (steve.rockwood@jax.org) is requesting a report.  

    He would like a list of alleles in MGI that have attached to them more than 10 
    references with a publication year of equal to or later than 2010. These 
    alleles may have additional references prior to 2010.

    The report should contain:
    1)allele symbol
    2)allele MGI ID
    3)number of allele references current year -1 or later
    4)total number of allele references

    This is to prioritize and solicit new strains to JAX that may be of interest to 
    multiple users.

    Is it possible to then take this list of alleles and compare it to the IMSR 
    database and list in a fifth column if this allele exists already in a 
    repository strain?
# History:
#
# sc	06/27/2012
#	- created
#
'''
 
import sys 
import os
import db
import reportlib
import string
import mgi_utils

try:
    if os.environ['DB_TYPE'] == 'postgres':
        import pg_db
        db = pg_db
        db.setTrace()
        db.setAutoTranslateBE()
    else:
        import db
except:
    import db

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

currentDate = mgi_utils.date('%Y')

db.useOneConnection(1)

fp = reportlib.init(sys.argv[0], printHeading = None, outputdir = os.environ['QCOUTPUTDIR'])

#
# First create a lookup of alleles, to their Facilities in imsr
#
results = db.sql('''select distinct a._Allele_key, f.abbrevName
        from ALL_Allele a, imsr..StrainFacilityAssoc sfa, imsr..SGAAssoc sga, imsr..Accession ac, imsr..Facility f, ACC_Accession ma 
        where a._Allele_key = ma._Object_key 
        and ma._LogicalDB_key = 1  
        and ma._MGIType_key = 11  
        and ma.private = 0  
        and ma.accID = ac.accID 
        and ac._IMSRType_key = 3 
        and ac._Object_key = sga._Allele_key 
        and sga._Strain_key = sfa._Strain_key 
        and sfa._Facility_key = f._Facility_key''', 'auto')
# and sfa._StrainState_key <> 2
imsrDict = {}
for r in results:
    aKey = r['_Allele_key']
    facility = r['abbrevName']
    if not imsrDict.has_key(aKey):
	imsrDict[aKey] = []
    imsrDict[aKey].append(facility)

# 
# get all allele references 
#
db.sql('''select distinct mra._Refs_key, mra._Object_key as _Allele_key
    into #aRefs
    from MGI_Reference_Assoc mra
    where mra._MGIType_key = 11
    order by mra._Object_key''', None)
db.sql('''create index idx1 on #aRefs(_Refs_key)''', None)

#
# get refernece counts for each allele
#
results = db.sql(''' select _Allele_key, count(_Refs_key) as refsCount
    from #aRefs
    group by _Allele_key''', 'auto')

#
# create a lookup of reference counts for each allele
#
allRefsDict = {}
for r in results:
    allRefsDict[r['_Allele_key']] = r['refsCount']

#
# get counts of allele references whose publication date is >= currentDate - 1
#
db.sql('''select a._Allele_key, count(a._Refs_key) as refsCount
    into #dCounts
    from #aRefs a, BIB_Refs b
    where a._Refs_key = b._Refs_key
    and b.year >= (%s - 1)
    group by a._Allele_key''' % (currentDate), None)

#
# get the set that has at least 10 references >= currentDate - 1
#
db.sql('''select * 
    into #d10Counts
    from #dCounts
    where refsCount >= 10''', None)
db.sql('''create index idx3 on #d10Counts(_Allele_key)''', None)

#
# get allele accid and symbol, exclude wild type
#
results = db.sql('''select ar.*, a.accid, aa.symbol
    from #d10Counts ar, ACC_Accession a, ALL_Allele aa
    where ar._Allele_key = a._Object_key
    and a._MGIType_key = 11
    and a._LogicalDB_key = 1
    and a.preferred = 1
    and a.prefixPart = 'MGI:'
    and ar._Allele_key = aa._Allele_key
    and aa.isWildType = 0
    order by aa.symbol''', 'auto')

fp.write('Allele Symbol' + TAB)
fp.write('Allele MGI ID' + TAB)
fp.write('Number of Allele Refs >= %s' % (int(currentDate) - 1) + TAB)
fp.write('Total Allele Refs' + TAB)
fp.write('Facilities with strains carrying this mutation' + CRT)

for r in results:
    symbol = r['symbol']
    mgiID = r['accid']
    aKey = r['_Allele_key']
    allCt = 0
    if allRefsDict.has_key(aKey):
	allCt = allRefsDict[aKey]
    refsCount = r['refsCount']
    facilities = []
    if imsrDict.has_key(aKey):
	facilities = imsrDict[aKey]
    f = string.join(facilities, ', ')
    fp.write('%s%s%s%s%s%s%s%s%s%s' % (symbol, TAB, mgiID, TAB, refsCount, TAB, allCt, TAB, f, CRT) )

reportlib.finish_nonps(fp)	# non-postscript file
db.useOneConnection(0)

