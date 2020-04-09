
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
# sc	10/12/2017 
#	- TR12250 Littriage Project
#	exclude AP:NoImages tag (33436864)
# lec   10/22/2014
#       - TR11750/postres complient
#
# 12/02/2013	lec
#	- TR11457/fix error in query
#
# 09/08/2011	lec
#	- TR 10835; copied from GXD_Images.py
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

# py3 convert to tuple mapping each member of list to a string, then repr as
# string e.g. "('BMC Biochem', 'BMC Biol', and so on )"
# this can be plugged into the query which uses 'in'

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

print('journals: %s' % journals)
journalsSQL = repr(tuple(map(str, journals)))
print('journalsSQL: %s' % journalsSQL)
#
# Main
#

fp = reportlib.init(sys.argv[0], 'Phenotype Annotations Requiring Images', outputdir = os.environ['QCOUTPUTDIR'])

count = 0
fp.write(TAB + 'Journals Checked:' + CRT + 2*TAB)
for j in journals:
    fp.write(str.ljust(j, 25) + TAB)
    count = count + 1
    if count > 2:
      fp.write(CRT + 2*TAB)
      count = 0
fp.write(2*CRT)
fp.write('Excludes References with AP:NoImages Tag\n\n')
fp.write(str.ljust('J#', 12))
fp.write(str.ljust('PubMed', 12))
fp.write(str.ljust('MGI ID', 20))
fp.write(str.ljust('short_citation', 75) + CRT)
fp.write(str.ljust('--', 12))
fp.write(str.ljust('------', 12))
fp.write(str.ljust('------', 20))
fp.write(str.ljust('--------------', 75) + CRT)

#
# select references that:
#   a) have genotype annotations (_AnnotType_key = 1002)
#   b) journal in journal list
#   c) year > 2008
#   d) genotype is not associated with a phenotype image via the allele
#

#
# all references that contain journals with genotype annotations, etc.
# where there exists an image/pane association to the genotype/allele
#
db.sql('''
      select distinct b._Refs_key
      into temporary table exists
      from VOC_Annot a, VOC_Evidence e, BIB_Refs b, GXD_AlleleGenotype g
      where a._AnnotType_key = 1002
            and a._Annot_key = e._Annot_key
            and e._Refs_key = b._Refs_key
            and b.journal in %s 
            and b.year > 2008
            and a._Object_key = g._Genotype_key
            and exists (select 1 from IMG_ImagePane_Assoc_View v
            where v._MGIType_key = 11
            and v._ImageClass_key in (6481782)
            and g._Allele_key = v._Object_key)
        ''' % (journalsSQL), None)

db.sql('create index exists_idx1 on exists(_Refs_key)', None)

#
# all references that contain journals with genotype annotations, etc.
# where the references does *not* exist in the "exists" temp table
# where there does *not* exists an image/pane association to the genotype/allele
#
# references may appear in more than one genotype/allele combination
# but not in others.  we are only interested in those where the reference
# does not appear in *any* image pane/genotype/allele association.
#
db.sql('''
      select distinct b._Refs_key
      into temporary table refs 
      from VOC_Annot a, VOC_Evidence e, BIB_Refs b, GXD_AlleleGenotype g
      where a._AnnotType_key = 1002
            and a._Annot_key = e._Annot_key
            and e._Refs_key = b._Refs_key
            and b.journal in %s 
            and b.year > 2008
            and a._Object_key = g._Genotype_key
            and not exists (select 1 from exists r where b._Refs_key = r._Refs_key)
            and not exists (select 1 from IMG_ImagePane_Assoc_View v
            where v._MGIType_key = 11
            and v._ImageClass_key in (6481782)
            and g._Allele_key = v._Object_key)
        ''' % (journalsSQL), None)

db.sql('create index refs_idx1 on refs(_Refs_key)', None)

results = db.sql('''
        select r._Refs_key, b.jnumID, b.short_citation, b.pubmedID, b.mgiID
        from refs r, BIB_Citation_Cache b
        where r._Refs_key = b._Refs_key
              and b.pubmedID is not null
        and not exists (select 1
        from BIB_Workflow_Tag t
        where r._Refs_key = t._Refs_key
        and t._Tag_key = 33436864)
        order by b.jnumID
        ''', 'auto')

for r in results:
    fp.write(str.ljust(r['jnumID'], 12))
    fp.write(str.ljust(r['pubmedID'], 12))
    fp.write(str.ljust(r['mgiID'], 20))
    fp.write(str.ljust(r['short_citation'], 75))
    fp.write(CRT)

fp.write(CRT + 'Total J numbers: ' + str(len(results)) + CRT)

reportlib.finish_nonps(fp)
