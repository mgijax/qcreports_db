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
# lec   03/08/2021
#       TR13398 - Creative Commons license issues (Part IV)
#
# sc	12/30/2019
#	- TR13205/move  to J Neurosci section and rename to 'Check copyright & 6 month delay'
#	    J Cell Biol
#	    J Exp Med
#	    J Gen Physiol
#
# lec	09/10/2018
#	- TR12954/new journal : eNeuro
#
'''
 
import sys
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

byPublisher = [
'Brain Res Gene Expr Patterns',
'Dev Biol', 
'Dev Dyn', 
'Development', 
'Direct Data Submission from Genetic Resource Science',
'Gene Expr Patterns', 
'Genesis', 
'J Biol Chem', 
'J Clin Invest',
'J Comp Neurol', 
'J Lipid Res', 
'Mech Dev', 
'Cells Dev', 
'Mol Reprod Dev',
'Proc Natl Acad Sci U S A'
]

byCreativeComments = [
'Acta Neuropathol Commun',
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
'Breast Cancer Res',
'Cell Commun Signal',
'Cell Death Dis',
'Cell Rep',
'Cells',
'Commun Biol',
'Dis Model Mech',
'eNeuro',
'Elife',
'EMBO Mol Med',
'Front Aging Neurosci',
'Front Behav Neurosci',
'Front Cell Dev Biol',
'Front Cell Neurosci',
'Front Genet',
'Front Immunol',
'Front Mol Neurosci',
'Front Neurosci',
'Front Physiol',
'Genome Biol',
'Int J Mol Sci',
'iScience',
'J Biol', 
'J Biomed Sci',
'JCI Insight',
'Mol Brain',
'Mol Metab',
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
'Sci Adv',
'Sci Rep',
'Stem Cell Reports',
'Vasc Cell'
]

# journals where year >= 2006
by2006 = ['Nucleic Acids Res', 'DNA Res']

byHybrid = [
'Acta Biochim Biophys Sin (Shanghai)',
'Biol Reprod',
'Br J Cancer',
'Brain',
'Carcinogenesis',
'Cardiovasc Res',
'Cereb Cortex',
'Chem Senses',
'Cell Death Differ',
'Cell Mol Immunol',
'Cell Res',
'Cell Tissue Res',
'Chromosoma',
'Chromosome Res',
'Eur J Hum Genet',
'Gene Ther',
'Glycobiology',
'Hum Mol Genet',
'Hum Reprod',
'J Gerontol A Biol Sci Med Sci',
'Mol Biol Evol',
'Toxicol Sci',
'Genes Immun',
'Hypertens Res',
'Int J Obes (Lond)',
'J Hum Genet',
'Lab Invest',
'Leukemia',
'Mucosal Immunol',
'Oncogene',
'Pediatr Res',
'Transgenic Res'
]

byOtherHybrid = [
'Cell Cycle', 
'EMBO J', 
'EMBO Rep', 
'J Invest Dermatol', 
'Immunol Cell Biol',
'Mol Cell Biol', 
'Mol Psychiatry',
'Am J Hum Genet',
'Biochem Biophys Res Commun',
'Differentiation',
'Eur J neurosci',
'FASEB J',
'FEBS Lett',
'J Cell Sci',
'Mol Cell Neurosci'
]

byCopyrightDelay = [
'J Neurosci', 
'J Cell Biol',
'J Exp Med',
'J Gen Physiol'
]

def runreport(fp, assayType):

    count = 0
    fp.write(TAB + 'By Publisher permission:' + CRT + 2*TAB)
    for j in byPublisher:
        fp.write(str.ljust(j, 25) + TAB)
        count = count + 1
        if count > 2:
          fp.write(CRT + 2*TAB)
          count = 0
    fp.write(2*CRT)

    fp.write(TAB + str.ljust('J#', 12))
    fp.write(str.ljust('short_citation', 75))
    fp.write(str.ljust('figure labels', 50) + CRT)
    fp.write(TAB + str.ljust('--', 12))
    fp.write(str.ljust('--------------', 75))
    fp.write(str.ljust('-------------', 50) + CRT)

    byPublisherIn = '\'' + '\',\''.join(byPublisher) + '\''
    print('byPublisherIn: %s' % byPublisherIn)

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
                and b.journal in (%s)
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
          ''' % (assayType, byPublisherIn), None)

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
                and b.journal in (%s)
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
          ''' % (assayType, byPublisherIn), None)

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

    fp.write(CRT + 'Total J numbers: ' + str(count) + CRT*4)

    #
    # Hybrid
    # Other Hybrid
    #

    count = 0
    fp.write(TAB + 'Hybrid Oxford and Springer Nature:' + CRT + 2*TAB)
    for j in byHybrid:
        fp.write(str.ljust(j, 25) + TAB)
        count = count + 1
        if count > 2:
          fp.write(CRT + 2*TAB)
          count = 0
    fp.write(2*CRT)

    count = 0
    fp.write(TAB + 'By Other Hybrid:' + CRT + 2*TAB)
    for j in byOtherHybrid:
        fp.write(str.ljust(j, 25) + TAB)
        count = count + 1
        if count > 2:
          fp.write(CRT + 2*TAB)
          count = 0
    fp.write(2*CRT)

    byHybridIn = '\'' + '\',\''.join(byHybrid) + '\''
    print('byHybridIn: %s' % byHybridIn)

    byOtherHybridIn = '\'' + '\',\''.join(byOtherHybrid) + '\''
    print('byOtherHybridIn: %s' % byOtherHybridIn)

    byJournal = byHybridIn + ',' + byOtherHybridIn

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
                and b.journal in (%s)
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
                and exists (select 1 from MGI_Note n
                        where i._Image_key = n._Object_key 
                        and n._NoteType_key = 1023
                        and n._MGIType_key = 9)
          ''' % (assayType, byJournal), None)

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
                and b.journal in (%s)
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
                and exists (select 1 from MGI_Note n
                        where r._Image_key = n._Object_key 
                        and n._NoteType_key = 1023
                        and n._MGIType_key = 9)
          ''' % (assayType, byJournal), None)

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
    
    fp.write(CRT + 'Total J numbers: ' + str(count) + CRT*4)

    #
    # TR13205: 'Check copyright & 6 month delay'
    #

    fp.write(TAB + 'Check copyright & 6 month delay:' + CRT)
    for j in byCopyrightDelay:
        fp.write(2*TAB + j + CRT)
    fp.write(2*CRT)

    byCopyrightDelayIn = '\'' + '\',\''.join(byCopyrightDelay) + '\''
    print('byCopyrightDelayIn: %s' % byCopyrightDelayIn)

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
                and b.journal in (%s)
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
                and exists (select 1 from MGI_Note n
                        where i._Image_key = n._Object_key 
                        and n._NoteType_key = 1023
                        and n._MGIType_key = 9)
          ''' % (assayType, byCopyrightDelayIn), None)

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
                and b.journal in (%s)
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
                and exists (select 1 from MGI_Note n
                        where r._Image_key = n._Object_key 
                        and n._NoteType_key = 1023
                        and n._MGIType_key = 9)
          ''' % (assayType, byCopyrightDelayIn), None)

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
            print(r)
            fp.write(TAB + str.ljust(r['jnumID'], 12))
            fp.write(str.ljust(r['short_citation'], 75))
            fp.write(str.ljust(','.join(fLabels[r['_Refs_key']]), 50) + CRT)
            refprinted.append(r['_Refs_key'])
            count = count + 1
    
    fp.write(CRT + 'Total J numbers: ' + str(count) + CRT*4)

    # TR13398 - Creative Commons license issues (Part IV)
    # Other hybrid journals using Creative Commons licenses
    # search for any copyright that isn’t from a journal listed in any of the above sections

    fp.write(TAB + 'Full open access using Creative commons licenses' + 2*CRT + 2*TAB)

    for j in byCreativeComments:
        fp.write(str.ljust(j, 25) + TAB)
        count = count + 1
        if count > 2:
          fp.write(CRT + 2*TAB)
          count = 0
    fp.write(2*CRT)

    byCreativeCommentsIn = '\'' + '\',\''.join(byCreativeComments) + '\''
    print('byCreativeCommentsIn: %s' % byCreativeCommentsIn)

    by2006In = '\'' + '\',\''.join(by2006) + '\''
    print('by2006In: %s' % by2006In)

    fp.write(TAB + 'Journals > 2006:' + CRT)
    for j in by2006:
        fp.write(2*TAB + j + CRT)
    fp.write(2*CRT)

    db.sql('''
          select distinct a._Refs_key, a.creation_date 
          into temporary table refs5
          from GXD_Assay a, BIB_Refs b, ACC_Accession ac, 
               IMG_Image i, IMG_ImagePane p
          where a._AssayType_key %s in (1,2,3,4,5,6,8,9) 
                and a._ImagePane_key = p._ImagePane_key 
                and p._Image_key = i._Image_key 
                and i.xDim is NULL 
                and a._Refs_key = b._Refs_key 
                and (b.journal in (%s)
                    or (b.journal in (%s) and year >= 2006)) 
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
                and exists (select 1 from MGI_Note n
                        where i._Image_key = n._Object_key 
                        and n._NoteType_key = 1023
                        and n._MGIType_key = 9
                        )
          ''' % (assayType, byCreativeCommentsIn, by2006In), None)

    db.sql('''
          insert into refs5
          select distinct a._Refs_key, a.creation_date 
          from GXD_Assay a, BIB_Refs b, ACC_Accession ac, 
               GXD_Specimen g, GXD_ISResultImage_View r
          where a._AssayType_key %s in (1,2,3,4,5,6,8,9) 
                and a._Assay_key = g._Assay_key 
                and g._Specimen_key = r._Specimen_key 
                and r.xDim is NULL 
                and a._Refs_key = b._Refs_key 
                and (b.journal in (%s)
                    or (b.journal in (%s) and year >= 2006)) 
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
                and exists (select 1 from MGI_Note n
                        where r._Image_key = n._Object_key 
                        and n._NoteType_key = 1023
                        and n._MGIType_key = 9
                        )
          ''' % (assayType, byCreativeCommentsIn, by2006In), None)

    db.sql('create index refs5_idx1 on refs5(_Refs_key)', None)

    results = db.sql('''
            select distinct r._Refs_key, rtrim(i.figureLabel) as figureLabel
            from refs5 r, IMG_Image i
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
        from refs5 r, BIB_All_View b
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
    
    fp.write(CRT + 'Total J numbers: ' + str(count) + CRT*4)

    # 
    # all other journals that contain copyright 'creative commons'
    #

    fp.write(TAB + 'All other journals that contain copyright = "creative commons"' + 2*CRT)

    byJournal = byPublisherIn + ',' + byHybridIn + ',' + byOtherHybridIn + ',' + byCopyrightDelayIn + ',' + byCreativeCommentsIn + ',' + by2006In

    sql = '''
          select distinct a._Refs_key, a.creation_date 
          into temporary table refs6
          from GXD_Assay a, BIB_Refs b, ACC_Accession ac, 
               IMG_Image i, IMG_ImagePane p
          where a._AssayType_key %s in (1,2,3,4,5,6,8,9) 
                and a._ImagePane_key = p._ImagePane_key 
                and p._Image_key = i._Image_key 
                and i.xDim is NULL 
                and a._Refs_key = b._Refs_key 
                and b.journal not in (%s)
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
          ''' % (assayType, byJournal)

    sql += '''\nand exists (select 1 from MGI_Note n
                        where i._Image_key = n._Object_key
                        and n._NoteType_key = 1023
                        and n._MGIType_key = 9
                        and n.note ilike '%creative commons%')
          '''
    db.sql(sql, None)

    sql = '''
          insert into refs6
          select distinct a._Refs_key, a.creation_date 
          from GXD_Assay a, BIB_Refs b, ACC_Accession ac, 
               GXD_Specimen g, GXD_ISResultImage_View r
          where a._AssayType_key %s in (1,2,3,4,5,6,8,9) 
                and a._Assay_key = g._Assay_key 
                and g._Specimen_key = r._Specimen_key 
                and r.xDim is NULL 
                and a._Refs_key = b._Refs_key 
                and b.journal not in (%s)
                and a._Assay_key = ac._Object_key 
                and ac._MGIType_key = 8 
          ''' % (assayType, byJournal)

    sql += '''\nand exists (select 1 from MGI_Note n
                        where r._Image_key = n._Object_key
                        and n._NoteType_key = 1023
                        and n._MGIType_key = 9
                        and n.note ilike '%creative commons%')
          '''
    db.sql(sql, None)

    db.sql('create index refs6_idx1 on refs5(_Refs_key)', None)

    results = db.sql('''
            select distinct r._Refs_key, rtrim(i.figureLabel) as figureLabel
            from refs6 r, IMG_Image i
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
        from refs6 r, BIB_All_View b
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
    
    fp.write(CRT + 'Total J numbers: ' + str(count) + CRT*4)

    db.sql('drop table refs',None)
    db.sql('drop table refs3',None)
    db.sql('drop table refs4',None)
    db.sql('drop table refs5',None)
    db.sql('drop table refs6',None)

#
# main
#

fp1 = reportlib.init(sys.argv[0], 'Papers Requiring Images', outputdir = os.environ['QCOUTPUTDIR'])
runreport(fp1, '')
reportlib.finish_nonps(fp1)

fp2 = reportlib.init('RECOMB_Images', 'Papers Requiring Images', outputdir = os.environ['QCOUTPUTDIR'])
runreport(fp2, 'not ')
reportlib.finish_nonps(fp2)

