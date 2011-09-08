#!/usr/local/bin/python

'''
#
# PHENO_Images.py
#
# Report:
#       Produce a report of all J numbers from the journals listed
#	that are cross-referenced to Alleles but do not have images
#       attached to them.
#
# Usage:
#       PHENO_Images.py
#
# Notes:
#
# History:
#
# 09/08/2011	lec
#	- TR 10835; copied from GXD_Images.py
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

journals = [
'BMC Biochem',
'BMC Biol',
'BMC Biotechnol',
'BMC Cancer',
'BMC Cell Biol',
'BMC Complement Altern Med',
'BMC Dev Biol',
'BMC Evol Biol',
'BMC Genet',
'BMC Genomics',
'BMC Med',
'BMC Mol Biol',
'BMC Neurosci',
'BMC Ophthalmol',
'BMC Res Notes',
'Genesis',
'J Biol Chem',
'J Cell Biol',
'J Clin Invest',
'J Comp Neurol',
'J Exp Med',
'J Gen Physiol',
'J Lipid Res',
'Mamm Genome',
'Mol Reprod Dev',
'PLoS Biol',
'PLoS Genet',
'PLoS Med',
'PLoS ONE',
'Proc Natl Acad Sci U S A'
]

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Phenotype Annotations Requiring Images', outputdir = os.environ['QCOUTPUTDIR'])

count = 0
fp.write(TAB + 'Journals Checked:' + CRT + 2*TAB)
for j in journals:
    fp.write(string.ljust(j, 25) + TAB)
    count = count + 1
    if count > 2:
      fp.write(CRT + 2*TAB)
      count = 0
fp.write(2*CRT)

fp.write(TAB + string.ljust('J#', 12))
fp.write(string.ljust('PubMed', 12))
fp.write(string.ljust('short_citation', 75) + CRT)
fp.write(TAB + string.ljust('--', 12))
fp.write(string.ljust('------', 12))
fp.write(string.ljust('--------------', 75) + CRT)

#
# select references that:
#   a) have genotype annotations (_AnnotType_key = 1002)
#   b) journal in journal list
#   c) year > 2008
#   d) genotype is not associated with a phenotype image
#

db.sql('''
      select distinct b._Refs_key
      into #refs 
      from VOC_Annot a, VOC_Evidence e, BIB_Refs b
      where a._AnnotType_key = 1002
	    and a._Annot_key = e._Annot_key
            and e._Refs_key = b._Refs_key
	    and b.journal in ("'%s'") 
	    and b.year > 2008
	    and not exists (select 1 from IMG_ImagePane_Assoc_View v
	    where v._MGIType_key = 11
	    and v._ImageClass_key in (6481782)
	    and a._Object_key = v._Object_key)
	''' % (string.join(journals, '","')), None)

db.sql('create index idx1 on #refs(_Refs_key)', None)

results = db.sql('''
	select r._Refs_key, b.jnumID, b.short_citation, b.pubmedID
	from #refs r, BIB_Citation_Cache b
	where r._Refs_key = b._Refs_key
        order by b.jnumID
	''', 'auto')

for r in results:
    fp.write(TAB + string.ljust(r['jnumID'], 12))
    fp.write(string.ljust(r['pubmedID'], 12))
    fp.write(string.ljust(r['short_citation'], 75))
    fp.write(CRT)

fp.write(CRT + 'Total J numbers: ' + str(len(results)) + CRT)

reportlib.finish_nonps(fp)
