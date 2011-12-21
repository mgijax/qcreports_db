#!/usr/local/bin/python

'''
#
# TR 9970
#
# Report:
#
#    MGI Allele_ID
#    allele symbol
#    allele name
#    allele category (e.g. spontaneous, targeted(floxed/frt), etc).
#    marker symbol
#    marker name
#    affected anatomical systems (as shown on Allele Summary page, comma separated)
#    similar human diseases (as shown on Allele Summary page, comma separated).
#    number of publications for the allele.
#    IMSR repository abbreviations for the "exact allele" 
#    (for what we show in the Allele Detail page as "carrying this mutation:
#    mouse strains: # available -- but instead of for example, giving "4", 
#    state JAX,JAX,EMMA,MMRRC). 
#
#
# Usage:
#       ALL_Jax_Report.py
#
# Notes:
#
# History:
#
# 12/21/2011	lec
#	- convert to outer join
#
# mhall	12/15/2009
#	- TR 9970- created
#
#
'''

import sys
import os
import string
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

db.useOneConnection(1)

fp = reportlib.init(sys.argv[0], 'All Jax Report', outputdir = os.environ['QCOUTPUTDIR'])

results = db.sql('''select distinct gag._Allele_key as 'key', vt.term 
	from VOC_AnnotHeader vah, voc_term vt, GXD_AlleleGenotype gag
	where vah.isNormal = 0 and vah._Term_key = vt._Term_key 
	and vah._Object_key = gag._Genotype_key
	order by vah._Object_key''', 'auto')

phenoTerms = {}

for row in results:
	if row['key'] not in phenoTerms:
		phenoTerms[row['key']] = row['term']
	else:
		phenoTerms[row['key']] = phenoTerms[row['key']] + ', ' + row['term']

cmds = []

cmds.append('''select a._Allele_key, gag._Genotype_key 
	into #tmp_geno
	from all_allele a 
	     LEFT OUTER JOIN GXD_AlleleGenotype gag on (a._Allele_key = gag._Allele_key)
	''')


cmds.append('''select distinct tg._Allele_key as 'key', vt.term + ' ' + aa.accID as 'term' 
	from #tmp_geno tg, voc_annot va, voc_term vt, acc_accession aa
	where va._Object_key = tg._Genotype_key and va._AnnotType_key = 1005 and va._Term_key != null
	and va._Term_key = vt._Term_key and va._Term_key = aa._Object_key and aa._MGIType_key = 13
	order by _Allele_key ''')

results = db.sql(cmds, 'auto')

omimTerms = {}

for row in results[1]:
	if row['key'] not in omimTerms:
		omimTerms[row['key']] = row['term']
	else:
		omimTerms[row['key']] = omimTerms[row['key']] + ', ' + row['term']


results = db.sql('''select _Object_key as 'key', count (distinct _Refs_key) as 'term'
	from MGI_Reference_Assoc where _MGIType_key = 11 group by _Object_key ''', 'auto')

refCount = {}

for row in results:
	if row['key'] not in refCount:
		refCount[row['key']] = row['term']
	else:
		refCount[row['key']] = refCount[row['key']] + ', ' + row['term']
		
results = db.sql('''select a._Allele_key as 'key', f.abbrevName as 'term'
	from all_allele a, acc_accession aa, imsr..StrainAGAccCache isac, imsr..StrainFacilityAssoc sfa,
	imsr..Facility f
	where a._Transmission_key != 3982953
	and a._Allele_key = aa._Object_key
	and aa._MGIType_key = 11 and aa.prefixPart = 'MGI:' and aa.private = 0 and aa.preferred = 1
	and aa.accID = isac.accID 
	and isac._Strain_key = sfa._Strain_key
	and sfa._Facility_key = f._Facility_key
	order by a._Allele_key ''', 'auto')

facility = {}

for row in results:
	if row['key'] not in facility:
		facility[row['key']] = row['term']
	else:
		facility[row['key']] = facility[row['key']] + ', ' + row['term']		

results = db.sql('''select a.accID, aa.symbol as 'asymbol', aa.name as 'aname',
	vt.term as 'alltype',  mm.symbol as 'msymbol', mm.name as 'mname', aa._Allele_key, convert(char(20), aa.creation_date, 107) as create_date 
	from all_allele aa, voc_term vt, mrk_marker mm, ACC_Accession a
	where aa._allele_type_key = vt._term_key and aa._Transmission_key != 3982953
	and aa._Marker_key = mm._Marker_key and aa._Allele_key = a._Object_key and aa.name != 'wild type'
	and a._MGIType_key = 11 and a.prefixPart = 'MGI:' and a.private = 0 and a.preferred = 1
    and aa._Allele_Status_key in (847114, 3983021) 
    order by aa.creation_date DESC''', 'auto')

fp.write('MGI Allele ID' + TAB)
fp.write('Allele Symbol' + TAB)
fp.write('Allele Name' + TAB)
fp.write('Allele Type' + TAB)
fp.write('Marker Symbol' + TAB)
fp.write('Marker Name' + TAB)
fp.write('Affected Anatomical Systems' + TAB)
fp.write('Similar Human Diseases' + TAB)
fp.write('Number of Publications' + TAB)
fp.write('IMSR Repository Abbreviation' + TAB)
fp.write('Creation Date' + CRT)

for r in results:
    fp.write(r['accID'] + TAB)
    fp.write(r['asymbol'] + TAB)
    fp.write(r['aname'] + TAB)
    fp.write(r['alltype'] + TAB)
    fp.write(r['msymbol'] + TAB)
    fp.write(r['mname'] + TAB)
    
    if r['_Allele_key'] in phenoTerms:
		fp.write(phenoTerms[r['_Allele_key']].replace(" phenotype", "")  + TAB)
    else:
    	fp.write('' + TAB)
    	
    if r['_Allele_key'] in omimTerms:
		fp.write(omimTerms[r['_Allele_key']]  + TAB)
    else:
    	fp.write('' + TAB)    	
    	
    if r['_Allele_key'] in refCount:
		fp.write(str(refCount[r['_Allele_key']])  + TAB)
    else:
    	fp.write('0' + TAB)      	
    
    if r['_Allele_key'] in facility:
		fp.write(str(facility[r['_Allele_key']])  + TAB)
    else:
    	fp.write('' + TAB)
    
    fp.write(r['create_date'] + CRT)	

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)
