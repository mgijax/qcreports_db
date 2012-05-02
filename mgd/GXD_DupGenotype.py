#!/usr/local/bin/python

"""
# TR 5488
#
# Report: This report was intended to do clean up of duplicate genotypes in
#         GXD.  Specifically the request was to provide a list of all duplicate
#         genotypes, that is, all genotypes with an identical strain and
#         allele pairs.
#
#         This is actually a multi step process which will require fetching
#         all genotypes with a match to another genotype on strain, and an
#         allele pair, that also has the same number of allele pairs.  Once
#         this list is acquired it needs to be turned into a distinct list of
#         genotype sets.  Then we must go through each of these sets and
#         try to match up their remaining allele pairs.  If everything matches
#         then we include this set, otherwise, we toss it.
#
# Ouput:
#       The resulting report should include per-line the mgi ids for the set
#       of genotypes and the strain and one of the allele pairs.  A line should
#       be included for each allele pair that is part of this set.
#  
# Usage:
#       tr5538.py
#
# History:
#
# dow	02/09/2004
#		- created
#
"""

import sys
import os
import string
import db
import reportlib

CRT = reportlib.CRT
TAB = reportlib.TAB

#
# genoTypeCompare:
# Compares two genotypes and determines if they are the same.
#
# The definition of two genotypes being the same is whether or not
# the have the same strain, and whether or not all of their associated
# allele pairs map to an allele pair in the other genotype.
#
# assumptions:
# Assumes that the strain has already been matched
# Assumes that the numAllelePairs represents the number of allele pairs
# associated with each genotype
# Assumes the structure of the genotype dictionaries that are passed in.
#
# returns 1 if the match, 0 if they do not.
#
def genoTypeCompare( geno1, geno2, numAllelePairs ):
    #  Counter of the number of allele pairs matched between genotypes
    matchCount = 0

    #
    # Compare each allele pair in genotype 1 to each allele pair in genotype 2
    # if a match is found the match counter is incremented.
    #
    for i in range(numAllelePairs):
        for j in range(numAllelePairs):
            if geno1['alleles'][i] == geno2['alleles'][j]:
                matchCount = matchCount + 1
                break
    #
    #  If the number of matches is equal to the number of allele pairs,
    #  then the genotypes are the same.
    #
    if matchCount == numAllelePairs:
        return 1
    else:
        return 0

#
# formatOutput:
# Formats the genotype set for output to a report.
# Will write the 2 genotypes and the strain at the head of each row.
# Genotypes that have mulitple allele pairs will be written as subsequent rows.
#
# assumptions:
# Assumes the format of the genoTypeSet dictionary.
#
# returns a formatted, tab-delimited string to be written to a report.
#
def formatOutput( genoTypeSet ):
    output = ''

    #
    #  Execute query and generate the "line header"  will be written with each pair of
    #  associated alleles
    #

    #
    #  Get accession id for genotype 1
    #
    results = db.sql('''
		select accID 
                from GXD_Genotype g, ACC_Accession ac 
                where g._GenoType_key = %s
                and g._GenoType_key = ac._Object_key 
                and ac._MGIType_key = 12 
                and ac.prefixPart = 'MGI:' 
                and ac.preferred = 1
		''' % (str(genoTypeSet['geno1']['key'])), 'auto')
    head = results[0]['accID'] + TAB

    #
    #  Get accession id for genotype 2
    #
    results = db.sql('''
		select accID 
                from GXD_Genotype g, ACC_Accession ac 
                where g._GenoType_key = %s
                and g._GenoType_key = ac._Object_key 
                and ac._MGIType_key = 12 
                and ac.prefixPart = 'MGI:' 
                and ac.preferred = 1
		''' % (str(genoTypeSet['geno2']['key'])), 'auto')
    head = head + results[0]['accID'] + TAB
    
    #
    #  Get strain name associated with genotypes
    #
    results = db.sql('''
		select strain 
		from PRB_Strain 
		where _Strain_key = %s
		''' % (str(genoTypeSet['strain'])), 'auto')
    head = head + results[0]['strain'] + TAB

    #
    #  Get allele symbols associated with all the allele pairs.
    #
    alleles = genoTypeSet['geno1']['alleles']
    for allelepair in alleles:
        cmd = 'select symbol from ALL_Allele where _Allele_key in ('
	
	if allelepair[0] != None:
	    cmd = cmd + str(allelepair[0]) + ','
	cmd = cmd + str(allelepair[1]) + ')'
        results = db.sql(cmd, 'auto')

        output = output + head
        for row in results:
            output = output + row['symbol'] + TAB
        output = output + CRT
        
    return output
    

#
# Main
#

#
#  Begin setting up report
#
fp = None

fp = reportlib.init(sys.argv[0], 'Duplicate Genotypes', os.environ['QCOUTPUTDIR'])

#
#  This query will fetch pairs of genotpes that have the same associated
#  strain and at least one common allele pair between them.  They should
#  also have the same total number of associated allele pairs.
#
db.sql('''select g1._Genotype_key as geno1, 
                 g2._Genotype_key as geno2, 
                 g1._Strain_key as strain 
          into #pairs 
          from GXD_Genotype g1, GXD_Genotype g2, GXD_AllelePair a1, GXD_AllelePair a2 
          where g1._Genotype_key = a1._Genotype_key and 
                a1._Allele_key_1 = a2._Allele_key_1 and 
                (a1._Allele_key_2 = a2._Allele_key_2 or 
                (a1._Allele_key_2 is null and 
                a2._Allele_key_2 is null)) and 
                a1._PairState_key = a2._PairState_key and 
                a2._Genotype_key = g2._Genotype_key and 
                g2._Strain_key = g1._Strain_key and 
	        g1.isConditional = g2.isConditional and 
                g1._Genotype_key != g2._Genotype_key and 
                (select count(distinct _AllelePair_key) 
                     from GXD_AllelePair ap 
                     where ap._Genotype_key = g1._Genotype_key) = 
                (select count(distinct _AllelePair_key) 
                     from GXD_AllelePair ap 
                     where ap._Genotype_key = g2._Genotype_key)
	''', None)

#
#  Now add entries that have the allele pairs transposed, but still match.
#
db.sql('''insert #pairs 
          select g1._Genotype_key as geno1, 
                 g2._Genotype_key as geno2, 
                 g1._Strain_key as strain 
          from GXD_Genotype g1, GXD_Genotype g2, GXD_AllelePair a1, GXD_AllelePair a2 
          where g1._Genotype_key = a1._Genotype_key and 
                a1._Allele_key_1 = a2._Allele_key_2 and 
                a1._Allele_key_2 = a2._Allele_key_1 and 
                a1._PairState_key = a2._PairState_key and 
                a2._Genotype_key = g2._Genotype_key and 
                g2._Strain_key = g1._Strain_key and 
	        g1.isConditional = g2.isConditional and 
                g1._Genotype_key != g2._Genotype_key and 
                (select count(distinct _AllelePair_key) 
                      from GXD_AllelePair ap 
                      where ap._Genotype_key = g1._Genotype_key) = 
                (select count(distinct _AllelePair_key) 
                      from GXD_AllelePair ap 
                      where ap._Genotype_key = g2._Genotype_key)
	  ''', None)

#
#  We now pull the genotype pair, associated strain, and a count of the number
#  of allele pairs (this number is used in processing later.
#
#  Excecute query
#
results = db.sql('''select p.geno1, p.geno2, p.strain, 
            count(distinct _AllelePair_key) as numPairs 
            from #pairs p, GXD_AllelePair gap 
            where p.geno1 = gap._Genotype_key 
            group by p.geno1, p.geno2
	    ''', 'auto')

#
#  Now cycle through and create a distinct set of genotype pairs.
#
genoDict = {}  # Dictionary of distinct genotype pairs

for row in results:
    geno1 = row['geno1']                     #  Genotype 1
    geno2 = row['geno2']                     #  Genotype 2

    #
    #  Create a tuple to use as a key to the genotype dictionary.
    #  The tuple will include the pair of genotype keys and be sorted,
    #  so that should we find the combination of genotypes in the opposite
    #  order we won't end up with a duplicate.
    #
    genoList = [geno1, geno2]
    genoList.sort()
    genoTuple = (genoList[0], genoList[1])

    #  The value of our genotype pair (all of it's attributes)
    value = {}

    #  A genotype has a key, and a set of allele pairs.
    genotype1 = {}
    genotype1['key'] = geno1
    genotype1['alleles'] = []
    value['geno1'] = genotype1
    genotype2 = {}
    genotype2['key'] = geno2
    genotype2['alleles'] = []
    value['geno2'] = genotype2
    
    value['numPairs'] = row['numPairs']
    value['strain'] = row['strain']
    genoDict[genoTuple] = value

#
#  Now cycle through and get all of the allele pairs for each genotype.
#
for key in genoDict.keys():
    genotypeSet = genoDict[key]
    geno1 = genotypeSet['geno1']
    geno2 = genotypeSet['geno2']
    geno1Alleles = geno1['alleles']
    geno2Alleles = geno2['alleles']
    cmds = []
    cmds.append('select _Allele_key_1, _Allele_key_2 from GXD_AllelePair where _GenoType_key = ' + str(geno1['key']))
    cmds.append('select _Allele_key_1, _Allele_key_2 from GXD_AllelePair where _GenoType_key = ' + str(geno2['key']))
    results = db.sql(cmds, 'auto')

    #
    #  Turn allele pairs into tuples so that they are easier to compare later.
    #
    for row in results[0]:
        alleles = [row['_Allele_key_1'], row['_Allele_key_2']]
        alleles.sort()
        alleleTuple = (alleles[0], alleles[1])
        geno1Alleles.append(alleleTuple)
    geno1['alleles'] = geno1Alleles 

    for row in results[1]:
        alleles = [row['_Allele_key_1'], row['_Allele_key_2']]
        alleles.sort()
        alleleTuple = (alleles[0], alleles[1])
        geno2Alleles.append(alleleTuple)
    geno2['alleles'] = geno2Alleles

#
#  Cycle through genotype pairs and compare them.  If they are equivalennt
#  write them to our report.  Otherwise delete them from our dictionary.
#
rows = 0
for key in genoDict.keys():
    genotypeSet = genoDict[key]
    if (genoTypeCompare(genotypeSet['geno1'], genotypeSet['geno2'], genotypeSet['numPairs'])):
        fp.write(formatOutput(genotypeSet))
	rows = rows + 1
    else:
        del genoDict[key]
                        
fp.write('\n(%d rows affected)\n' % (rows))

#
# now do a check for the genotypes that have strains only (no genotypes)
#

db.sql('''select g._Genotype_key, g._Strain_key
	into #genotype
	from GXD_Genotype g
	where not exists (select 1 from GXD_AllelePair p
		where g._Genotype_key = p._Genotype_key)
	''', None)

db.sql('''select g.*
	into #duplicate
	from #genotype g
	group by g._Strain_key having count(*) > 1
	''', None)

results = db.sql('''select a.accID, s.strain
	from #duplicate d, PRB_Strain s, ACC_Accession a
	where d._Strain_key = s._Strain_key
	and d._Genotype_key = a._Object_key
	and a._MGIType_key = 12
	and a.prefixPart = "MGI:"
	and a.preferred = 1
	''', 'auto')

fp.write('\n\nDuplicate Genotypes where there is no Allele (strain only)\n\n')

for r in results:
    fp.write(r['accID'] + TAB + TAB + r['strain'] + CRT)

reportlib.finish_nonps(fp)

