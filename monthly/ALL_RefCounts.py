
'''
#
# Report:
#    12/04/2023 : checked with Cindy and this is still used, we think
#    jason.beckwith@jax.org is requesting a report.  
#
#    The report should contain:
#
#    1) allele symbol
#
#    2) allele MGI ID
#
#    3) number of allele references with MGI-creation-date within 2 years of the run date of this report
#
#    4) total number of allele references
#
#    5) IMSR facilities : JAX always comes first
#
#    This is to prioritize and solicit new strains to JAX that may be of interest to 
#    multiple users.
#
#    Is it possible to then take this list of alleles and compare it to the IMSR 
#    database and list in a fifth column if this allele exists already in a 
#    repository strain?
#
# History:
#
# kstone 12/17/2014
#	Replaced IMSR query with IMSR strains file from solr
#
# lec   10/22/2014
#       - TR11750/postres complient
#	contains calls to IMSR
#
# lec	04/28/2014
#	- TR11667/see TR for details
#
# sc	06/27/2012
#	- created
#
'''
 
import csv
import sys 
import os
import mgi_utils
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

IMSR_CSV = os.environ['IMSR_STRAINS_CSV']

# functions

def createImsrDict1():
        """
        Returns dictionary of allele IDs to facility abbreviation
        for JAX only
        """
        facilityMap = {}
        csvfile = open(IMSR_CSV, 'r')
        reader = csv.reader(csvfile)
        for row in reader:
                allele_ids = row[0]
                provider = row[3]
                if allele_ids and provider == 'JAX':
                        for id in  allele_ids.split(','):
                                facilityMap[id] = ['JAX']
        
        return facilityMap

def createImsrDict2():
        """
        Returns dictionary of allele IDs to facility abbreviation
        for non-JAX 
        """
        facilityMap = {}
        csvfile = open(IMSR_CSV, 'r')
        reader = csv.reader(csvfile)
        for row in reader:
                allele_ids = row[0]
                provider = row[3]
                if allele_ids and provider != 'JAX':
                        for id in  allele_ids.split(','):
                                facilityMap.setdefault(id, []).append(provider)
        
        return facilityMap

currentDate = mgi_utils.date('%Y')

fp = reportlib.init(sys.argv[0], printHeading = None, outputdir = os.environ['QCOUTPUTDIR'])

# create the mappings of allele MGI ID to facility abbreviation
imsrDict1 = createImsrDict1()
imsrDict2 = createImsrDict2()

# 
# get all allele references 
#
db.sql('''select distinct mra._Refs_key, mra._Object_key as _Allele_key
    into temporary table aRefs
    from MGI_Reference_Assoc mra
    where mra._MGIType_key = 11
    order by mra._Object_key''', None)
db.sql('''create index idx1 on aRefs(_Refs_key)''', None)

#
# get refernece counts for each allele
#
results = db.sql(''' select _Allele_key, count(_Refs_key) as refsCount
    from aRefs
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
    into temporary table dCounts
    from aRefs a, BIB_Refs b
    where a._Refs_key = b._Refs_key
    and date_part('year', b.creation_date) between (%s - 1) and %s
    and b.journal != 'Database Download'
    group by a._Allele_key''' % (currentDate, currentDate), None)

#
# get the set that has at least 10 references >= currentDate - 1
#
db.sql('''select * 
    into temporary table d10Counts
    from dCounts
    where refsCount >= 10''', None)
db.sql('''create index idx3 on d10Counts(_Allele_key)''', None)

#
# get allele accid and symbol, exclude wild type
#
results = db.sql('''select ar.*, a.accid, aa.symbol
    from d10Counts ar, ACC_Accession a, ALL_Allele aa
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
fp.write('Number of Allele Refs between %s and %s' % (int(currentDate) - 1, int(currentDate)) + TAB)
fp.write('Total Allele Refs' + TAB)
fp.write('Facilities with strains carrying this mutation' + CRT)

for r in results:

    symbol = r['symbol']
    mgiID = r['accid']
    aKey = r['_Allele_key']

    allCt = 0
    if aKey in allRefsDict:
        allCt = allRefsDict[aKey]

    refsCount = r['refsCount']

    facilities = []
    if mgiID in imsrDict1:
        facilities = imsrDict1[mgiID]
    f1 =  ', '.join(facilities)

    facilities = []
    if mgiID in imsrDict2:
        # need to unique and sort the list of providers
        facilities = list(set(imsrDict2[mgiID]))
        facilities.sort()
    f2 =  ', '.join(facilities)

    if len(f1) > 0 and len(f2) > 0:
        f1 = f1 + ', '

    fp.write('%s%s%s%s%s%s%s%s%s%s%s' % (symbol, TAB, mgiID, TAB, refsCount, TAB, allCt, TAB, f1, f2, CRT) )

reportlib.finish_nonps(fp)	# non-postscript file
