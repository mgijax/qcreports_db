#!/usr/local/bin/python

"""
# GXD_GenotypeRef.py
#
# Report: This report is for the purposes of doing cleanup of jnumbers that
#         have had seperate genotypes added both via GXD and A&P curators.
#         The intent of the report is to find all genotypes with the same jnum
#         and the same allele pairs, but different strains.  
#
# Ouput:
#       The resulting report should include per-line the JNumber and
#       the strain names of the two differing strains with the same
#       alleles.
#  
# Usage:
#       
#	GXD_GenotypeRef.py
#
# History:
#
# lec	03/01/2004
#	- converted to qc report per TR 5595
#
# dow	02/20/2004
#	- created, TR 5489
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
# The definition of two genotypes being the same is whether or not all
# of their associated allele pairs map to an allele pair in the other genotype.
#
# assumptions:
# Assumes the structure of the genotype dictionaries that are passed in.
#
# returns 1 if the match, 0 if they do not.
#
def genoTypeCompare( geno1, geno2 ):

    #
    # If allele lengths are different, then there's no match
    #
    if len(geno1['alleles']) != len(geno2['alleles']):
	return 0

    #
    # If any allele from genotype 1 is not in genotype 2, then no match
    #
    for a in geno1['alleles']:
	if a not in geno2['alleles']:
	    return 0

    #
    # If any allele from genotype 2 is not in genotype 1, then no match
    #
    for a in geno2['alleles']:
	if a not in geno1['alleles']:
	    return 0

    return 1
    
#
# Main
#

#
#  Begin setting up report
#
fp = reportlib.init(sys.argv[0], 'Duplicate Genotypes', outputdir = os.environ['QCREPORTOUTPUTDIR'])

cmds = []

#
#  This query will fetch pairs of genotpes that have different associated
#  strains and at least one common allele pair between them.  They should
#  also have the same total number of associated allele pairs.
#

cmds.append('select g1._Genotype_key as geno1, ' +
            'g2._Genotype_key as geno2, ' +
	    'g1._Strain_key as strain1, ' +
	    'g2._Strain_key as strain2, ' +
            'ga._Refs_key ' +
            'into #prepairs ' +
            'from GXD_Genotype g1, GXD_Genotype g2, ' +
            'GXD_AlleleGenotype a1, GXD_AlleleGenotype a2, ' +
	    'GXD_Expression ge, GXD_Assay ga, VOC_Evidence ve, VOC_Annot va, VOC_AnnotType vt ' +
            'where g1._Genotype_key = a1._Genotype_key and ' +
            'a1._Allele_key = a2._Allele_key and ' +
            'a2._Genotype_key = g2._Genotype_key and ' +
            'g2._Strain_key != g1._Strain_key and ' +
            '(select count(distinct _Allele_key) ' +
            'from GXD_AlleleGenotype ap ' +
            'where ap._Genotype_key = g1._Genotype_key) = ' +
            '(select count(distinct _Allele_key) ' +
            'from GXD_AlleleGenotype ap ' +
            'where ap._Genotype_key = g2._Genotype_key) ' +
	    'and ge._Genotype_key = g1._Genotype_key ' +
	    'and ge._Assay_key = ga._Assay_key ' +
	    'and ga._Refs_key = ve._Refs_key ' +
	    'and ve._Annot_key = va._Annot_key ' +
	    'and va._Object_key = g2._Genotype_key ' +
	    'and va._AnnotType_key = vt._AnnotType_key ' +
            'and vt.name = "PhenoSlim/Genotype" ')

cmds.append('create nonclustered index idx_geno1 on #prepairs(geno1)')
cmds.append('create nonclustered index idx_geno2 on #prepairs(geno2)')
cmds.append('create nonclustered index idx_strain1 on #prepairs(strain1)')
cmds.append('create nonclustered index idx_strain2 on #prepairs(strain2)')
cmds.append('create nonclustered index idx_ref on #prepairs(_Refs_key)')

# Resolve the Strains and JNum

cmds.append('select distinct p.*, b.accID as jnumID, ' +
            'substring(s1.strain,1,50) as AandPStrain, substring(s2.strain,1,50) as GXDStrain ' +
	    'into #pairs ' +
	    'from #prepairs p, BIB_Acc_VIew b, PRB_Strain s1, PRB_Strain s2 ' +
	    'where p._Refs_key = b._Object_key ' +
	    'and b.prefixPart = "J:" ' +
	    'and p.strain1 = s1._Strain_key ' +
	    'and p.strain2 = s2._Strain_key')

# Cache the Allele key and Symbol

cmds.append('select distinct a.symbol, a._Allele_key from #pairs p, GXD_AlleleGenotype g, ALL_Allele a ' +
	    'where p.geno1 = g._Genotype_key ' +
	    'and g._Allele_key = a._Allele_key ' +
	    'union ' +
            'select distinct a.symbol, a._Allele_key from #pairs p, GXD_AlleleGenotype g, ALL_Allele a ' +
	    'where p.geno2 = g._Genotype_key ' +
	    'and g._Allele_key = a._Allele_key ')

# Cache the Allele keys


cmds.append('select distinct g._Genotype_key, g._Allele_key from #pairs p, GXD_AlleleGenotype g ' +
	    'where p.geno1 = g._Genotype_key ' +
	    'union ' +
            'select distinct g._Genotype_key, g._Allele_key from #pairs p, GXD_AlleleGenotype g ' +
	    'where p.geno2 = g._Genotype_key ')

#
#  We now pull the genotype pair, associated strain
#
cmds.append('select distinct jnumID, geno1, geno2, AandPStrain, GXDStrain from #pairs p order by jnumID')

#
#  Excecute query
#
results = db.sql(cmds, 'auto')

#
# Cache the Allele key and symbol
#
asymbol = {}
for r in results[-3]:
    asymbol[r['_Allele_key']] = r['symbol']

#
# Cache the Allele keys
#
alleles = {}
for r in results[-2]:
    key = r['_Genotype_key']
    value = r['_Allele_key']
    if not alleles.has_key(key):
	alleles[key] = []
    alleles[key].append(value)

#
#  Now cycle through and create a distinct set of genotype pairs.
#
genoDict = {}  # Dictionary of distinct genotype pairs

for row in results[-1]:
    geno1 = row['geno1']                     #  Genotype 1
    geno2 = row['geno2']                     #  Genotype 2
    jnumID = row['jnumID']

    #
    #  Create a tuple to use as a key to the genotype dictionary.
    #
    genoList = [jnumID, geno1, geno2]
    genoTuple = (genoList[0], genoList[1], genoList[2])

    #  The value of our genotype pair (all of it's attributes)
    value = {}

    #  A genotype has a key, and a set of allele pairs.
    genotype1 = {}
    genotype1['key'] = geno1
    genotype1['alleles'] = alleles[geno1]
    value['geno1'] = genotype1

    genotype2 = {}
    genotype2['key'] = geno2
    genotype2['alleles'] = alleles[geno2]
    value['geno2'] = genotype2

    value['jnumID'] = row['jnumID']
    value['AandPStrain'] = row['AandPStrain']
    value['GXDStrain'] = row['GXDStrain']
    genoDict[genoTuple] = value

#
#  Cycle through genotype pairs and compare them.  If they are equivalennt
#  write them to our report.  Otherwise delete them from our dictionary.
#
rows = 0
keySort = genoDict.keys()
keySort.sort()

for key in keySort:
    genotypeSet = genoDict[key]
    if (genoTypeCompare(genotypeSet['geno1'], genotypeSet['geno2'])):

        fp.write(string.ljust(genotypeSet['jnumID'], 15) + 
		 string.ljust(genotypeSet['AandPStrain'], 55) +
                 string.ljust(genotypeSet['GXDStrain'], 55))

        for a in genotypeSet['geno1']['alleles']:
	    fp.write(string.ljust(asymbol[a], 35))

	fp.write(CRT)
	rows = rows + 1
    else:
        del genoDict[key]
                        
fp.write('\n(%d rows affected)\n' % (rows))
reportlib.finish_nonps(fp)

