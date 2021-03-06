

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
# sc	12/30/2019
#	- TR13205/move  to J Neurosci section and rename to
#    'Check copyright & 6 month delay'
#	    J Cell Biol
#	    J Exp Med
#	    J Gen Physiol
#
# lec	09/10/2018
#	- TR12954/new journal : eNeuro
#
# lec	02/09/2017
#	- TR12505/new journal : Biol Open, Cell Cycle
#
# lec	11/07/2016
#	- TR12449/new journal : J Neurosci
#
# lec	08/19/2015
#	- TR11963/new journal : Dis Model Mech
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
#	- TR 8826; added PLoS One
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

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

journals = [
'Biol Open',
'BMC Bioinformatics',
'BMC Biochem', 
'BMC Biol', 
'BMC Biotechnol', 
'BMC Blood Disord',
'BMC Cancer', 
'BMC Cell Biol', 
'BMC Complement Altern Med',
'BMC Dev Biol', 
'BMC Evol Biol', 
'BMC Gastroenterol',
'BMC Genet', 
'BMC Genomics', 
'BMC Immunol',
'BMC Med', 
'BMC Med Genet',
'BMC Mol Biol', 
'BMC Nephrol',
'BMC Neurosci',
'BMC Ophthalmol', 
'BMC Pharmacol Toxicol',
'BMC Physiol',
'BMC Res Notes',
'BMC Struct Biol',
'BMC Syst Biol',
'Brain Res Gene Expr Patterns',
'Breast Cancer Res',
'Cell Commun Signal',
'Cell Death Dis',
'Cell Rep',
'Dev Biol', 
'Dev Dyn', 
'Development', 
'Direct Data Submission from Genetic Resource Science',
'Dis Model Mech',
'eNeuro',
'Elife',
'Exp Mol Med',
'Gene Expr Patterns', 
'Genesis', 
'Genome Biol',
'J Biol', 
'J Biol Chem', 
'J Biomed Sci',
'J Clin Invest',
'J Comp Neurol', 
'J Lipid Res', 
'Mech Dev', 
'Mol Reprod Dev',
'Nat Commun',
'Neural Dev',
'PeerJ',
'PLoS Biol', 
'PLoS Comput Biol',
'PLoS Curr',
'PLoS Genet', 
'PLoS Med', 
'PLoS Negl Trop Dis',
'PLoS One' ,
'PLoS Pathog',
'Proc Natl Acad Sci U S A',
'Sci Rep',
'Vasc Cell'
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
'Cell Cycle', 'EMBO J', 'J Invest Dermatol', 'Mol Psychiatry'
]

checkCpyrtAndDelay = [
'J Neurosci', 
'J Cell Biol',
'J Exp Med',
'J Gen Physiol']

def runreport(fp, assayType):

    count = 0
    fp.write(TAB + 'Journals Checked:' + CRT + 2*TAB)
    for j in journals:
        fp.write(str.ljust(j, 25) + TAB)
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

    fp.write(TAB + str.ljust('J#', 12))
    fp.write(str.ljust('short_citation', 75))
    fp.write(str.ljust('figure labels', 50) + CRT)
    fp.write(TAB + str.ljust('--', 12))
    fp.write(str.ljust('--------------', 75))
    fp.write(str.ljust('-------------', 50) + CRT)

    #
    # journals1 = journals
    # journals2 = journals2005
    # journals3 = journals2006
    #
    #journals1 = '\'' + ','.join(journals) + '\''
    journals1 =  repr(tuple(map(str, journals)))
    # check if list is single, if so tuple will have trailing ','
    if len(journals) == 1:
        journals1 = journals1.replace(',','')
    print('journals1: %s' % journals1)

    #journals2 = '\'' + ','.join(journals2005) + '\''
    journals2 = repr(tuple(map(str, journals2005)))
    if len(journals2005) == 1:
        journals2 = journals2.replace(',','')
    print('journals2: %s' % journals2)

    #journals3 = '\'' + ','.join(journals2006) + '\''
    journals3 = repr(tuple(map(str, journals2006)))
    if len(journals2006) == 1:
        journals3 = journals3.replace(',','')
    print('journals3: %s' % journals3)

    db.sql('''
          select distinct a._Refs_key, a.creation_date 
          into temporary table refs 
          from GXD_Assay a, BIB_Refs b, ACC_Accession ac, 
               IMG_Image i, IMG_ImagePane p 
          where a._AssayType_key %s in (1,2,3,4,5,6,8,9) 
                and a._ImagePane_key = p._ImagePane_key 
                and p._Image_key = i._Image_key 
                and i.xDim is NULL 
                and a._Refs_key = b._Refs_key 
                and ((b.journal in %s) 
                    or (b.journal in %s and year >= 2005)
                    or (b.journal in %s and year >= 2006))
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
          ''' % (assayType, journals1, journals2, journals3), None)

    db.sql('''
          insert into refs
          select distinct a._Refs_key, a.creation_date 
          from GXD_Assay a, BIB_Refs b, ACC_Accession ac, 
               GXD_Specimen g, GXD_ISResultImage_View r 
          where a._AssayType_key %s in (1,2,3,4,5,6,8,9) 
                and a._Assay_key = g._Assay_key 
                and g._Specimen_key = r._Specimen_key 
                and r.xDim is NULL 
                and a._Refs_key = b._Refs_key 
                and ((b.journal in %s) 
                    or (b.journal in %s and year >= 2005) 
                    or (b.journal in %s and year >= 2006)) 
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
          ''' % (assayType, journals1, journals2, journals3), None)

    db.sql('create index refs_idx1 on refs(_Refs_key)', None)

    results = db.sql('''
            select distinct r._Refs_key, rtrim(i.figureLabel) as figureLabel
            from refs r, IMG_Image i
            where r._Refs_key = i._Refs_key
            order by figureLabel
            ''', 'auto')
    fLabels = {}
    for r in results:
        key = r['_Refs_key']
        value = r['figureLabel']
        if key not in fLabels:
            fLabels[key] = []
        fLabels[key].append(value)

    results = db.sql('''
            select r._Refs_key, b.jnumID, b.short_citation 
            from refs r, BIB_All_View b
            where r._Refs_key = b._Refs_key 
            order by r.creation_date, b.jnumID
            ''', 'auto')

    count = 0
    refprinted = []
    for r in results:
        if r['_Refs_key'] not in refprinted:
            fp.write(TAB + str.ljust(r['jnumID'], 12))
            fp.write(str.ljust(r['short_citation'], 75))
            fp.write(str.ljust(','.join(fLabels[r['_Refs_key']]), 50) + CRT)
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
    #journals4 = '\'' + ','.join(journalsOxford) + '\''
    journals4 = repr(tuple(map(str, journalsOxford)))
    if len(journalsOxford) == 1:
        journals4 = journals4.replace(',','')
    print('journals4: %s' % journals4)

    #journals5 = '\'' + ','.join(journalsOther) + '\''
    journals5 = repr(tuple(map(str, journalsOther)))
    if len(journalsOther) == 1:
        journals5 = journals5.replace(',','')
    print('journals5: %s' % journals5)

    db.sql('''
          select distinct a._Refs_key, a.creation_date 
          into temporary table refs3
          from GXD_Assay a, BIB_Refs b, ACC_Accession ac, 
               IMG_Image i, IMG_ImagePane p
          where a._AssayType_key %s in (1,2,3,4,5,6,8,9) 
                and a._ImagePane_key = p._ImagePane_key 
                and p._Image_key = i._Image_key 
                and i.xDim is NULL 
                and a._Refs_key = b._Refs_key 
                and (b.journal in %s or b.journal in %s)
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
                and exists (select 1 from MGI_Note n, MGI_NoteChunk c
                where i._Image_key = n._Object_key 
                and n._NoteType_key = 1023
                and n._MGIType_key = 9
                and n._Note_key = c._Note_key)
          ''' % (assayType, journals4, journals5), None)

    db.sql('''
          insert into refs3
          select distinct a._Refs_key, a.creation_date 
          from GXD_Assay a, BIB_Refs b, ACC_Accession ac, 
               GXD_Specimen g, GXD_ISResultImage_View r
          where a._AssayType_key %s in (1,2,3,4,5,6,8,9) 
                and a._Assay_key = g._Assay_key 
                and g._Specimen_key = r._Specimen_key 
                and r.xDim is NULL 
                and a._Refs_key = b._Refs_key 
                and (b.journal in %s or b.journal in %s)
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
                and exists (select 1 from MGI_Note n, MGI_NoteChunk c
                where r._Image_key = n._Object_key 
                and n._NoteType_key = 1023
                and n._MGIType_key = 9
                and n._Note_key = c._Note_key)
          ''' % (assayType, journals4, journals5), None)

    db.sql('create index refs3_idx1 on refs3(_Refs_key)', None)

    results = db.sql('''
            select distinct r._Refs_key, rtrim(i.figureLabel) as figureLabel
            from refs3 r, IMG_Image i
            where r._Refs_key = i._Refs_key
            order by figureLabel
            ''', 'auto')
    fLabels = {}
    for r in results:
        key = r['_Refs_key']
        value = r['figureLabel']
        if key not in fLabels:
            fLabels[key] = []
        fLabels[key].append(value)

    results = db.sql('''
        select r._Refs_key, b.jnumID, b.short_citation 
        from refs3 r, BIB_All_View b
        where r._Refs_key = b._Refs_key 
        order by r.creation_date, b.jnumID
        ''', 'auto')

    count = 0
    refprinted = []
    for r in results:
        if r['_Refs_key'] not in refprinted:
            fp.write(TAB + str.ljust(r['jnumID'], 12))
            fp.write(str.ljust(r['short_citation'], 75))
            fp.write(str.ljust(','.join(fLabels[r['_Refs_key']]), 50) + CRT)
            refprinted.append(r['_Refs_key'])
            count = count + 1
    
    fp.write(CRT + 'Total J numbers: ' + str(count) + CRT*3)

    #
    # J Neurosci
    #

    fp.write(TAB + 'Check copyright & 6 month delay:' + CRT)
    for j in checkCpyrtAndDelay:
        fp.write(2*TAB + j + CRT)
    fp.write(2*CRT)

    #
    # journals6 = Check copyright & 6 month delay
    #
    #journals6 = '\'' + ','.join(checkCpyrtAndDelay) + '\''
    journals6 = repr(tuple(map(str, checkCpyrtAndDelay)))
    if len(checkCpyrtAndDelay) == 1:
        journals6 = journals6.replace(',','')
    print('journals6: %s' % journals6)

    db.sql('''
          select distinct a._Refs_key, a.creation_date 
          into temporary table refs4
          from GXD_Assay a, BIB_Refs b, ACC_Accession ac, 
               IMG_Image i, IMG_ImagePane p
          where a._AssayType_key %s in (1,2,3,4,5,6,8,9) 
                and a._ImagePane_key = p._ImagePane_key 
                and p._Image_key = i._Image_key 
                and i.xDim is NULL 
                and a._Refs_key = b._Refs_key 
                and b.journal in %s
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
                and exists (select 1 from MGI_Note n, MGI_NoteChunk c
                where i._Image_key = n._Object_key 
                and n._NoteType_key = 1023
                and n._MGIType_key = 9
                and n._Note_key = c._Note_key)
          ''' % (assayType, journals6), None)

    db.sql('''
          insert into refs4
          select distinct a._Refs_key, a.creation_date 
          from GXD_Assay a, BIB_Refs b, ACC_Accession ac, 
               GXD_Specimen g, GXD_ISResultImage_View r
          where a._AssayType_key %s in (1,2,3,4,5,6,8,9) 
                and a._Assay_key = g._Assay_key 
                and g._Specimen_key = r._Specimen_key 
                and r.xDim is NULL 
                and a._Refs_key = b._Refs_key 
                and b.journal in %s
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
                and exists (select 1 from MGI_Note n, MGI_NoteChunk c
                where r._Image_key = n._Object_key 
                and n._NoteType_key = 1023
                and n._MGIType_key = 9
                and n._Note_key = c._Note_key)
          ''' % (assayType, journals6), None)

    db.sql('create index refs4_idx1 on refs4(_Refs_key)', None)

    results = db.sql('''
            select distinct r._Refs_key, rtrim(i.figureLabel) as figureLabel
            from refs4 r, IMG_Image i
            where r._Refs_key = i._Refs_key
            order by figureLabel
            ''', 'auto')
    fLabels = {}
    for r in results:
        key = r['_Refs_key']
        value = r['figureLabel']
        if key not in fLabels:
            fLabels[key] = []
        fLabels[key].append(value)

    results = db.sql('''
        select r._Refs_key, b.jnumID, b.short_citation 
        from refs4 r, BIB_All_View b
        where r._Refs_key = b._Refs_key 
        order by r.creation_date, b.jnumID
        ''', 'auto')

    count = 0
    refprinted = []
    for r in results:
        if r['_Refs_key'] not in refprinted:
            fp.write(TAB + str.ljust(r['jnumID'], 12))
            fp.write(str.ljust(r['short_citation'], 75))
            fp.write(str.ljust(','.join(fLabels[r['_Refs_key']]), 50) + CRT)
            refprinted.append(r['_Refs_key'])
            count = count + 1
    
    fp.write(CRT + 'Total J numbers: ' + str(count) + CRT*3)

    db.sql('drop table refs',None)
    db.sql('drop table refs3',None)
    db.sql('drop table refs4',None)

#
# main
#

fp1 = reportlib.init(sys.argv[0], 'Papers Requiring Images', outputdir = os.environ['QCOUTPUTDIR'])
runreport(fp1, '')
reportlib.finish_nonps(fp1)

fp2 = reportlib.init('RECOMB_Images', 'Papers Requiring Images', outputdir = os.environ['QCOUTPUTDIR'])
runreport(fp2, 'not ')
reportlib.finish_nonps(fp2)
