#!/usr/local/bin/python

'''
#
# GXD_ImagesUnused.py
#
# Report:
#       TR 8429
#
#      The report should look at J numbers that are in the assay table (ie papers that 
#      have been "full coded.") For the image stubs associated with those J numbers, 
#      which image panes are not present in the assay table (ie which were entered but 
#      not used for full coding)?
# 
#      Fields for report:
#      MGI ID of image stub w/ unused panes (primary sort)
#      J number (secondary sort)
#      Figure Label of stub (tertiary sort)
#      Pane Label
# 
#      Please add a row count.
#
# Usage:
#
# Notes:
#
# History:
#
# lec	03/25/2009
#	- TR 9566; only select _MGIType_key = Assay (8)
#
# mhall	3/17/2009
#	- TR 9479; removed the restriction on null image panels
#
# lec	12/02/2008
#	- TR 9357; remove image stub check
#
# lec	09/09/2008
#	- TR 9251; exclude Cre
#
# lec	09/25/2007
#	- TR 8429
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

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Unused image panes from full coded references', outputdir = os.environ['QCOUTPUTDIR'])

#
# Select Gel Assays Image Panes that are full-coded.
# 	Images that are "not null"
#

db.sql('''
     select r._Refs_key, r.jnumID, a._ImagePane_key 
     into #gel 
     from GXD_Assay a, BIB_Citation_Cache r 
     where a._Refs_key = r._Refs_key 
     and a._AssayType_key in (1,2,3,4,5,6,8,9,10,11) 
     and a._ImagePane_key is not null
     ''', None)

db.sql('create index gel_idx1 on #gel(_Refs_key)', None)
db.sql('create index gel_idx2 on #gel(_ImagePane_key)', None)

#
# Select Specimen Image Panes that are full-coded.
#
# Specimen Images are:
#	Assay Types = 1 RNA in situ
#                     6 Immunohistochemistry
#                     9 In situ reporter (knock in)
#                     10 In situ reporter (transgenic)
#                     11 Recombinase reporter
#
#

db.sql('''
    select r._Refs_key, r.jnumID, p._ImagePane_key 
    into #specimen 
    from GXD_Assay a, BIB_Citation_Cache r, 
    GXD_Specimen s, GXD_InSituResult i, GXD_InSituResultImage p 
    where a._Refs_key = r._Refs_key 
    and a._AssayType_key in (1,6,9,10,11) 
    and a._Assay_key = s._Assay_key 
    and s._Specimen_key = i._Specimen_key 
    and i._Result_key = p._Result_key
    ''', None)

db.sql('create index specimen_idx1 on #specimen(_Refs_key)', None)
db.sql('create index specimen_idx2 on #specimen(_ImagePane_key)', None)

#
# Select Image Panes that are full-coded.
#      Reference exists (is used) in Assay table
#      Image Type = "Full Size"
#      Image MGI Type = "Assay" (8)
#
#

db.sql('''
     select r._Refs_key, r.jnumID, a._Image_key, a.figureLabel, aa._ImagePane_key, aa.paneLabel, 
     convert(char(10), aa.creation_date, 101) as cdate
     into #images 
     from IMG_Image a, BIB_Citation_Cache r, IMG_ImagePane aa 
     where exists (select 1 from GXD_Assay assay where a._Refs_key = assay._Refs_key 
     and assay._AssayType_key in (1,2,3,4,5,6,8,9)) 
     and a._Refs_key = r._Refs_key 
     and a._ImageType_key = 1072158 
     and a._MGIType_key = 8 
     and a._Image_key = aa._Image_key 
     ''', None)

db.sql('create index images_idx1 on #images(jnumID)', None)
db.sql('create index images_idx2 on #images(figureLabel)', None)

#
# From this list of Image Panes, select those that are not used
# in either the Specimen or Gel table.
#
# That is, select Images where some Panes have been full-coded,
# and some Image Panes have not been full-coded.
#
# Print in the:
#     MGI ID of the Image
#     J# of the Image
#     Figure Label
#     Image Pane
#     Creation date of Image Pane
#

results = db.sql('''
    select a.accID, i.jnumID, i.figureLabel, i.paneLabel, i.cdate 
    from #images i, ACC_Accession a 
    where not exists (select 1 from #specimen s 
    where i._Refs_key = s._Refs_key 
    and i._ImagePane_key = s._ImagePane_key) 
    and not exists (select 1 from #gel s 
    where i._Refs_key = s._Refs_key 
    and i._ImagePane_key = s._ImagePane_key) 
    and i._Image_key = a._Object_key 
    and a._MGIType_key = 9 
    and a._LogicalDB_key = 1 
    order by a.accID, i.jnumID, i.figureLabel
    ''', 'auto')

for r in results:
    fp.write(r['accID'] + TAB)
    fp.write(r['jnumID'] + TAB)
    fp.write(r['figureLabel'] + TAB)
    if (r['paneLabel'] == None):
    	fp.write('None' + TAB)
    else:
    	fp.write(r['paneLabel'] + TAB)
    fp.write(r['cdate'] + CRT)

fp.write(CRT + '(%d rows affected)' % (len(results)) + CRT)

reportlib.finish_nonps(fp)	# non-postscript file

