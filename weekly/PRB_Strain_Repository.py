
'''
#
# PRB_Strain_Repository.py
#
# Weekly metrics report for repository strains, 
# listing the cumulative number of unique publications (PMID IDs) 
# and total number of strains with PubMed references
#
# For each strain in MGI with an external ID (JAX Strain, MMRRC, EMMA etc...), please list:
# 1) The number of unique references (refs with any PubMed ID, in order to exclude submission and load refs))
# 2) The number of unique strains (by repository ID) per repository with a reference that has a PubMed ID
#
# History:
#
# lec   02/26/2026
#   wts2-1813/Report of Repostory strains: total associated publication numbers and total strains published
#
'''
 
import sys
import os
import reportlib
import db

db.setTrace()

TAB = reportlib.TAB
CRT = reportlib.CRT

fp = reportlib.init(sys.argv[0], 'Repostory strains: total associated publication numbers and total strains published', outputdir = os.environ['QCOUTPUTDIR'])

# references/strain associations where reference contains pubmed id
db.sql('''
    select distinct sf._refs_key, sf._Object_key
    into temp table strainrefs
    from MGI_Reference_Assoc sf, BIB_Citation_Cache c
    where sf._MGIType_key = 10
    and sf._Refs_key = c._Refs_key
    and c.pubmedid is not null
    ''', None)
db.sql('create index idxref on strainrefs(_Refs_key)', None)
db.sql('create index idxobj on strainrefs(_Object_key)', None)

#
# repository list is the same as that used in PWI/Strain module/Accession Types
# counts by reference 
# counts by strain (_object_key)
#
results = db.sql('''
    select ldb._Logicaldb_key, ldb.name, count(distinct sf._refs_key) as refCount, count(distinct sf._object_key) as strainCount
    from strainrefs sf, PRB_Strain s, ACC_Accession a, ACC_LogicalDB ldb
    where sf._Object_key = s._Strain_key
    and s._Strain_key = a._Object_key
    and a._MGIType_key = 10
    and a._Logicaldb_key in (22,37,38,39,40,54,56,57,58,70,71,83,84,87,90,91,93,94,154,161,177,184,188,200,202,206,207,208,213,215,216,217,219,220,221,224,232)
    and a._Logicaldb_key = ldb._Logicaldb_key
    group by 1,2
    order by ldb.name
    ''', 'auto')
for r in results:
    fp.write(r['name'] + ' Publication PubMed IDS ' + str(r['refCount']) + CRT)
    fp.write(r['name'] + ' strain primary identifiers ' + str(r['strainCount']) + 2*CRT)

reportlib.finish_nonps(fp)
