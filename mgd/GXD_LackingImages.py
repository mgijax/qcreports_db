#!/usr/local/bin/python

'''
#
# GXD_LackingImages.py
#
# Report:
#       Produce a report of all J numbers from the journals specified
#	that are full coded in GXD database but do not have images
#       attached to them.
#
# Usage:
#       GXD_LackingImages.py
#
# Notes:
#
# History:
#
# lec	03/03/2015
#	- TR11891/new journals
#	- RECOMB_LackingImages is exactly the same, except for query
#
# lec	10/07/2009
#	- TR 9876
#	1) split into two sections:  Genes&Development, Nature Publishing group
#	2) add column listing the date the image stub was created
#	3) sort by date of image stub, most recent at the top
#
# lec	08/20/2009
#	- TR 9770; Nat Methods, Nat Protoc
#
# lec	05/26/2009
#	- TR 9641; only select Full Size Images
#
# lec	04/16/2009
#	- TR 9616; add 'Genes Dev'
#
# lec	05/01/2008
#	- TR 8775; on select GXD assay types
#	- TR 8984; fix counts
#
# lec	01/13/2005
#	- TR 6480
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

journalsAll = [
'Biotechnology', 
'Cell Death Differ', 
'Nat Biotechnol', 
'Nat Cell Biol', 
'Nat Genet', 
'Nat Immunol', 
'Nat Med', 
'Nat Methods',
'Nat Neurosci', 
'Nat Protoc',
'Nat Rev Cancer', 
'Nat Rev Genet', 
'Nat Rev Immunol', 
'Nat Rev Mol Cell Bio', 
'Nat Rev Neurosci',
'Nat Struct Biol', 
'Nature',
'Oncogene',
'Genes Dev',
'Acta Pharmacol Sin',
'Bone Marrow Transplant',
'Br J Cancer',
'Cancer Gene Ther',
'Cell Mol Immunol',
'Cell Res',
'Eur J Clin Nutr',
'Eur J Hum Genet',
'Exp Mol Med',
'Eye (Lond)',
'Gene Ther',
'Genes Immun',
'Heredity (Edinb)',
'Hypertens Res',
'Immunol Cell Biol',
'Int J Obes (Lond)',
'Int J Oral Sci',
'J Cereb Blood Flow Metab',
'J Hum Genet',
'Lab Invest',
'Leukemia',
'Mucosal Immunol',
'Nat Chem Biol',
'Nat Rev Drug Discov',
'Nat Struct Mol Biol',
'Pediatr Res',
'Pharmacogenomics J',
'Prostate Cancer Prostatic Dis',
'Spinal Cord',
]

def printAll(fp):

    count = 0
    fp.write(TAB + 'Journals for all years:' + CRT + 2*TAB)
    for j in journalsAll:
        fp.write(string.ljust(j, 25) + TAB)
        count = count + 1
        if count > 2:
          fp.write(CRT + 2*TAB)
          count = 0
    fp.write(2*CRT)

def printFields(fp):

    fp.write(TAB + string.ljust('J#', 12))
    fp.write(string.ljust('short_citation', 60))
    fp.write(string.ljust('stub created', 15))
    fp.write(string.ljust('figure labels', 50) + CRT)
    fp.write(TAB + string.ljust('--', 12))
    fp.write(string.ljust('--------------', 60))
    fp.write(string.ljust('------------', 15))
    fp.write(string.ljust('-------------', 50) + CRT)

def printResults(fp):

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
        if not fLabels.has_key(key):
	    fLabels[key] = []
        fLabels[key].append(value)

    results = db.sql('''
	    select r._Refs_key, b.jnumID, b.short_citation, r.creation_date, r.cdate
	    from refs r, BIB_All_View b
	    where r._Refs_key = b._Refs_key 
	    order by r.creation_date desc, b.jnumID''', 'auto')

    count = 0
    refprinted = []
    for r in results:
        if r['_Refs_key'] not in refprinted:
            fp.write(TAB + string.ljust(r['jnumID'], 12))
            fp.write(string.ljust(r['short_citation'], 60))
	    fp.write(string.ljust(str(r['cdate']), 15))
            fp.write(string.ljust(string.join(fLabels[r['_Refs_key']], ','), 50) + CRT)
	    refprinted.append(r['_Refs_key'])
	    count = count + 1

    fp.write(CRT + 'Total J numbers: ' + str(count) + CRT*3)

    db.sql('drop table refs', None)

def selectOther():

    #
    # for journalsAll
    # select references of any year
    # for given assays (see below)
    # with full image stubs
    #

    db.sql('''
	    select distinct r._Refs_key, r.journal, i.creation_date, 
		   to_char(i.creation_date, 'MM/dd/yyyy') as cdate
	    into temporary table refs
	    from BIB_Refs r, GXD_Assay a, IMG_Image i
	    where r.journal in ('%s')
	    and r._Refs_key = a._Refs_key
	    and a._AssayType_key in (1,2,3,4,5,6,8,9)
	    and r._Refs_key = i._Refs_key 
	    and i._ImageType_key = 1072158
	    and i.xDim is null
	    ''' % (string.join(journalsAll, "','")), None)

    db.sql('create index refs_idx2 on refs(_Refs_key)', None)

def selectOther2():

    #
    # for journalsAll
    # select references of any year
    # for given assays (see below)
    # with full image stubs
    #

    db.sql('''
	    select distinct r._Refs_key, r.journal, i.creation_date, 
		   to_char(i.creation_date, 'MM/dd/yyyy') as cdate
	    into temporary table refs
	    from BIB_Refs r, GXD_Assay a, IMG_Image i
	    where r.journal in ('%s')
	    and r._Refs_key = a._Refs_key
	    and a._AssayType_key not in (1,2,3,4,5,6,8,9)
	    and r._Refs_key = i._Refs_key 
	    and i._ImageType_key = 1072158
	    and i.xDim is null
	    ''' % (string.join(journalsAll, "','")), None)

    db.sql('create index refs_idx2 on refs(_Refs_key)', None)

#
# Main
#

fp1 = reportlib.init(sys.argv[0], 'Papers Requiring Permissions', outputdir = os.environ['QCOUTPUTDIR'])
printAll(fp1)
printFields(fp1)
selectOther()
printResults(fp1)
reportlib.finish_nonps(fp1)

fp2 = reportlib.init('RECOMB_LackingImages', 'Papers Requiring Permissions', outputdir = os.environ['QCOUTPUTDIR'])
printAll(fp2)
printFields(fp2)
selectOther2()
printResults(fp2)
reportlib.finish_nonps(fp2)

