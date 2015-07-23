#!/usr/local/bin/python

'''
#
# GXD_Images.py
#
# Report:
#       Produce a report of all J numbers from the journals listed
#	that are cross-referenced to Assays but do not have images
#       attached to them.
#
# Usage:
#       GXD_Images.py
#
# Notes:
#
# History:
#
# lec	03/03/2015
#	- TR11891/new journals
#
# lec	01/23/2012
#	- TR10945/'EMBO J'
#
# lec	12/21/2011
#	- TR10930/Oxford journals
#
# lec	08/20/2009
#	- TR9770; Neural Develop changed to Neural Dev
#	  Breast Cancer Res
#	  Genome Biol
#	  J Biol
#
# lec	07/14/2009
#	- TR9717; added:
#	  BMC Res Notes
#
# lec   05/12/2009
#	- TR 9643; added:
#	  Cell Commun Signal
#	  J Biomed Sci
#	  Neural Develop
#	- alphabetize names
#
# lec	04/07/2009
#	- TR 9606; The jouranls:
#         Genesis
#	  J Comp Neurol
#	  Mol Reprod Dev
#	  
# lec	07/23/2008
#	- TR 9163; The journals:
#	  J Cell Biol
#	  J Exp Med
#	  J Gen Physiol
#
# lec	05/06/2008
#	- TR 8984; The journals are:
#         J Biol Chem
#         J Lipid Res
#         J Clin Invest
#
# lec	05/01/2008
#	- TR 8775; on select GXD assay types
#
# lec	03/04/2008
#	- TR 8826; added PLoS ONE
#
# lec	02/09/2007
#	- TR 8147; added Proc Natl Acad Sci U S A
#
# lec	09/28/2006
#	- TR 7925; added Nucleic Acids Res
#
# lec	10/18/2005
#	- remove restriction on Assay Type per Connie
#
# lec	12/17/2004
#	- TR 6424; added journals beginning "PLoS%" and "BMC%"
#
# lec	09/16/2004
#	- TR 6205; added Dev Dyn
#
# lec	03/05/2004
#	- converted to QC (TR 5636)
#
# dbm   12/4/2002
#       - created (TR 4296)
#
'''
 
import sys
import os
import string
import reportlib
import db

db.setTrace()
db.setAutoTranslateBE()

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
'Brain Res Gene Expr Patterns',
'Breast Cancer Res',
'Cell Commun Signal',
'Dev Biol', 
'Dev Dyn', 
'Development', 
'Gene Expr Patterns', 
'Genesis', 
'Genome Biol',
'J Biol', 
'J Biol Chem', 
'J Biomed Sci',
'J Cell Biol', 
'J Clin Invest',
'J Comp Neurol', 
'J Exp Med', 
'J Gen Physiol',
'J Lipid Res', 
'Mech Dev', 
'Mol Reprod Dev',
'Neural Dev',
'PLoS Biol', 
'PLoS Genet', 
'PLoS Med', 
'PLoS ONE' ,
'Proc Natl Acad Sci U S A',
'Cell Death Dis',
'Nat Commun',
'Sci Rep',
'Elife',
'Vasc Cell',
'PLoS Comput Biol',
'PLoS Curr',
'PLoS Negl Trop Dis',
'PLoS Pathog',
'PeerJ',
'BMC Bioinformatics',
'BMC Blood Disord',
'BMC Gastroenterol',
'BMC Immunol',
'BMC Med Genet',
'BMC Nephrol',
'BMC Pharmacol Toxicol',
'BMC Physiol',
'BMC Struct Biol',
'BMC Syst Biol',
'Direct Data Submission from Genetic Resource Science'
]

# journals where year >= 2005
journals2005 = ['Nucleic Acids Res']

# journals where year >= 2006
journals2006 = ['DNA Res']

#
# copyright checks
#  1) Oxford
#  2) all else
#

journalsOxford = [
'Acta Biochim Biophys Sin (Shanghai)',
'Brain',
'Carcinogenesis',
'Cardiovasc Res',
'Cereb Cortex',
'Chem Senses',
'Glycobiology',
'Hum Mol Genet',
'Hum Reprod',
'J Gerontol A Biol Sci Med Sci',
'Mol Biol Evol',
'Toxicol Sci',
]

journalsOther = [
'EMBO J', 'J Invest Dermatol', 'Mol Psychiatry'
]

def runreport(fp, assayType):

    count = 0
    fp.write(TAB + 'Journals Checked:' + CRT + 2*TAB)
    for j in journals:
        fp.write(string.ljust(j, 25) + TAB)
        count = count + 1
        if count > 2:
          fp.write(CRT + 2*TAB)
          count = 0
    fp.write(2*CRT)

    fp.write(TAB + 'Journals > 2005:' + CRT)
    for j in journals2005:
        fp.write(2*TAB + j + CRT)
    fp.write(CRT)
    
    fp.write(TAB + 'Journals > 2006:' + CRT)
    for j in journals2006:
        fp.write(2*TAB + j + CRT)
    fp.write(2*CRT)

    fp.write(TAB + string.ljust('J#', 12))
    fp.write(string.ljust('short_citation', 75))
    fp.write(string.ljust('figure labels', 50) + CRT)
    fp.write(TAB + string.ljust('--', 12))
    fp.write(string.ljust('--------------', 75))
    fp.write(string.ljust('-------------', 50) + CRT)

    #
    # journals1 = journals
    # journals2 = journals2005
    # journals3 = journals2006
    #
    journals1 = '\'' + string.join(journals, '\',\'') + '\''
    journals2 = '\'' + string.join(journals2005, '\',\'') + '\''
    journals3 = '\'' + string.join(journals2006, '\',\'') + '\''

    db.sql('''
          select distinct a._Refs_key, a.creation_date 
          into #refs 
          from GXD_Assay a, BIB_Refs b, ACC_Accession ac, 
               IMG_Image i, IMG_ImagePane p 
          where a._AssayType_key %s in (1,2,3,4,5,6,8,9) 
	        and a._ImagePane_key = p._ImagePane_key 
                and p._Image_key = i._Image_key 
                and i.xDim is NULL 
                and a._Refs_key = b._Refs_key 
	        and ((b.journal in (%s)) 
		    or (b.journal in (%s) and year >= 2005)
		    or (b.journal in (%s) and year >= 2006))
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
          ''' % (assayType, journals1, journals2, journals3), None)

    db.sql('''
          insert into #refs
          select distinct a._Refs_key, a.creation_date 
          from GXD_Assay a, BIB_Refs b, ACC_Accession ac, 
               GXD_Specimen g, GXD_ISResultImage_View r 
          where a._AssayType_key %s in (1,2,3,4,5,6,8,9) 
	        and a._Assay_key = g._Assay_key 
                and g._Specimen_key = r._Specimen_key 
                and r.xDim is NULL 
                and a._Refs_key = b._Refs_key 
	        and ((b.journal in (%s)) 
		    or (b.journal in (%s) and year >= 2005) 
		    or (b.journal in (%s) and year >= 2006)) 
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
          ''' % (assayType, journals1, journals2, journals3), None)

    db.sql('create index refs_idx1 on #refs(_Refs_key)', None)

    results = db.sql('''
	    select distinct r._Refs_key, rtrim(i.figureLabel) as figureLabel
	    from #refs r, IMG_Image i
	    where r._Refs_key = i._Refs_key
	    order by figureLabel
	    ''', 'auto')
    fLabels = {}
    for r in results:
        key = r['_Refs_key']
        value = r['figureLabel']
        if not fLabels.has_key(key):
	    fLabels[key] = []
        fLabels[key].append(value)

    results = db.sql('''
	    select r._Refs_key, b.jnumID, b.short_citation 
	    from #refs r, BIB_All_View b
	    where r._Refs_key = b._Refs_key 
            order by r.creation_date, b.jnumID
	    ''', 'auto')

    count = 0
    refprinted = []
    for r in results:
        if r['_Refs_key'] not in refprinted:
            fp.write(TAB + string.ljust(r['jnumID'], 12))
            fp.write(string.ljust(r['short_citation'], 75))
            fp.write(string.ljust(string.join(fLabels[r['_Refs_key']], ','), 50) + CRT)
	    refprinted.append(r['_Refs_key'])
	    count = count + 1

    fp.write(CRT + 'Total J numbers: ' + str(count) + CRT*3)

    #
    # Oxford Journals
    # Other Journals
    #

    fp.write(TAB + 'Oxford Journals Checked:' + CRT)
    for j in journalsOxford:
        fp.write(2*TAB + j + CRT)
    fp.write(CRT)
    fp.write(TAB + 'Other Journals Checked:' + CRT)
    for j in journalsOther:
        fp.write(2*TAB + j + CRT)
    fp.write(2*CRT)

    #
    # journal4 = Oxford Journals
    # journal5 = Others
    #
    journals4 = '\'' + string.join(journalsOxford, '\',\'') + '\''
    journals5 = '\'' + string.join(journalsOther, '\',\'') + '\''

    db.sql('''
          select distinct a._Refs_key, a.creation_date 
          into #refs3
          from GXD_Assay a, BIB_Refs b, ACC_Accession ac, 
               IMG_Image i, IMG_ImagePane p
          where a._AssayType_key %s in (1,2,3,4,5,6,8,9) 
	        and a._ImagePane_key = p._ImagePane_key 
                and p._Image_key = i._Image_key 
                and i.xDim is NULL 
                and a._Refs_key = b._Refs_key 
	        and (b.journal in (%s)
		or b.journal in (%s))
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
	        and exists (select 1 from MGI_Note n, MGI_NoteChunk c
	        where i._Image_key = n._Object_key 
	        and n._NoteType_key = 1023
	        and n._MGIType_key = 9
	        and n._Note_key = c._Note_key)
          ''' % (assayType, journals4, journals5), None)

    db.sql('''
          insert into #refs3
          select distinct a._Refs_key, a.creation_date 
          from GXD_Assay a, BIB_Refs b, ACC_Accession ac, 
               GXD_Specimen g, GXD_ISResultImage_View r
          where a._AssayType_key %s in (1,2,3,4,5,6,8,9) 
	        and a._Assay_key = g._Assay_key 
                and g._Specimen_key = r._Specimen_key 
                and r.xDim is NULL 
                and a._Refs_key = b._Refs_key 
	        and (b.journal in (%s)
		    or b.journal in (%s))
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
	        and exists (select 1 from MGI_Note n, MGI_NoteChunk c
	        where r._Image_key = n._Object_key 
	        and n._NoteType_key = 1023
	        and n._MGIType_key = 9
	        and n._Note_key = c._Note_key)
          ''' % (assayType, journals4, journals5), None)

    db.sql('create index refs3_idx1 on #refs3(_Refs_key)', None)

    results = db.sql('''
	    select distinct r._Refs_key, rtrim(i.figureLabel) figureLabel
	    from #refs3 r, IMG_Image i
	    where r._Refs_key = i._Refs_key
	    ''', 'auto')
    fLabels = {}
    for r in results:
        key = r['_Refs_key']
        value = r['figureLabel']
        if not fLabels.has_key(key):
	    fLabels[key] = []
        fLabels[key].append(value)

    results = db.sql('''
	select r._Refs_key, b.jnumID, b.short_citation 
	from #refs3 r, BIB_All_View b
	where r._Refs_key = b._Refs_key 
        order by r.creation_date, b.jnumID
	''', 'auto')

    count = 0
    refprinted = []
    for r in results:
        if r['_Refs_key'] not in refprinted:
            fp.write(TAB + string.ljust(r['jnumID'], 12))
            fp.write(string.ljust(r['short_citation'], 75))
            fp.write(string.ljust(string.join(fLabels[r['_Refs_key']], ','), 50) + CRT)
	    refprinted.append(r['_Refs_key'])
	    count = count + 1
    
    fp.write(CRT + 'Total J numbers: ' + str(count) + CRT*3)

    db.sql('drop table #refs',None)
    db.sql('drop table #refs3',None)

#
# main
#

fp1 = reportlib.init(sys.argv[0], 'Papers Requiring Images', outputdir = os.environ['QCOUTPUTDIR'])
runreport(fp1, '')
reportlib.finish_nonps(fp1)

fp2 = reportlib.init('RECOMB_Images', 'Papers Requiring Images', outputdir = os.environ['QCOUTPUTDIR'])
runreport(fp2, 'not ')
reportlib.finish_nonps(fp2)

