#!/usr/local/bin/python

'''
#
# TR 8368
#
# Report:
#
# One gene papers in the GXD literature index that have not been full coded.
# Display the following columns:
#
#    1) Gene symbol
#    2) New Gene - Y or N to indicate whether the gene is new (not found in
#                  any assay).
#    3) Priority - High, Medium or Low
#    4) E? - Y or N to indicate whether any IndexAssays have been annotated
#            with an E? (excluding "cDNA" and "Primer ex").
#    5) J Number
#    6) Short form of citation
#
# Order the reports by:
#
#    1) New gene
#    2) Priority
#    3) Gene symbol
#
# Usage:
#       GXD_OneGenePapers.py
#
# Notes:
#
# History:
#
# dbm	07/26/2007
#	- new
#
'''

import sys
import os
import string
import re
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], 'One gene papers', outputdir = os.environ['QCOUTPUTDIR'])

fp.write(2*CRT)

fp.write(string.ljust('Gene Symbol', 20))
fp.write(SPACE)
fp.write(string.ljust('New Gene', 8))
fp.write(SPACE)
fp.write(string.ljust('Priority', 10))
fp.write(SPACE)
fp.write(string.ljust('E?', 4))
fp.write(SPACE)
fp.write(string.ljust('J Number', 10))
fp.write(SPACE)
fp.write(string.ljust('Short Citation', 255))
fp.write(CRT)

fp.write(20*'-')
fp.write(SPACE)
fp.write(8*'-')
fp.write(SPACE)
fp.write(10*'-')
fp.write(SPACE)
fp.write(4*'-')
fp.write(SPACE)
fp.write(10*'-')
fp.write(SPACE)
fp.write(255*'-')
fp.write(CRT)

cmds = []
#
# Get one gene papers that have not been full coded.  If a paper is not full
# coded, it should be in the index, but not in any assay.
#
db.sql('select gi._Refs_key ' + \
       'into #included_papers ' + \
       'from GXD_Index gi ' + \
       'where not exists (select 1 ' + \
                         'from GXD_Assay ga ' + \
                         'where ga._Refs_key = gi._Refs_key) ' + \
       'group by gi._Refs_key ' + \
       'having count(gi._Refs_key) = 1', None)

#
# Get papers that only contain assay type "cDNA" and/or "Primer extension".
# These will be excluded from the results.
#
db.sql('select distinct gi._Refs_key ' + \
       'into #excluded_papers ' + \
       'from GXD_Index gi ' + \
       'where 0 = (select count(*) from GXD_Index_Stages gis ' + \
                  'where gi._Index_key = gis._Index_key ' + \
                  'and gis._IndexAssay_key != 74725 ' + \
                  'and gis._IndexAssay_key != 74728) ' + \
       'and exists (select 1 from GXD_Index_Stages gis ' + \
                   'where gi._Index_key = gis._Index_key ' + \
                   'and gis._IndexAssay_key in (74725, 74728))', None)

#
# Get the final list of papers for the report by excluding the ones that 
# are not needed.
#
db.sql('select gi._Index_key, gi._Refs_key, gi._Marker_key, ' + \
              'gi._Priority_key ' + \
       'into #papers1 ' + \
       'from GXD_Index gi, #included_papers ip ' + \
       'where gi._Refs_key = ip._Refs_key and ' + \
             'not exists (select 1 ' + \
                         'from #excluded_papers ep ' + \
                         'where ep._Refs_key = gi._Refs_key)', None)

#
# Add in the new gene indicator.
#
db.sql('select p1.*, 1 "new_gene" ' + \
       'into #papers2 ' + \
       'from #papers1 p1 ' + \
       'where not exists (select 1 from GXD_Assay ga ' + \
                         'where p1._Marker_key = ga._Marker_key) ' + \
       'union ' + \
       'select p1.*, 0 "new_gene" ' + \
       'from #papers1 p1 ' + \
       'where exists (select 1 from GXD_Assay ga ' + \
                      'where p1._Marker_key = ga._Marker_key)', None)

#
# Add in the E? annotation indicator.
#
db.sql('select p2.*, 0 "E_annot" ' + \
       'into #papers3 ' + \
       'from #papers2 p2 ' + \
       'where not exists (select 1 from GXD_Index_Stages gis ' + \
                         'where gis._Index_key = p2._Index_key and ' + \
                               'gis._StageID_key = 74769 and ' + \
                               'gis._IndexAssay_key not in (74725,74728)) ' + \
       'union ' + \
       'select p2.*, 1 "E_annot" ' + \
       'from #papers2 p2 ' + \
       'where exists (select 1 from GXD_Index_Stages gis ' + \
                     'where gis._Index_key = p2._Index_key and ' + \
                           'gis._StageID_key = 74769 and ' + \
                           'gis._IndexAssay_key not in (74725,74728))', None)

#
# Get the final results set for the report.
#
results = db.sql('select giv.symbol, p3.new_gene, vt.term, p3.E_annot, ' + \
                        'giv.jnumID, giv.short_citation ' + \
                 'from #papers3 p3, GXD_Index_View giv, VOC_Term vt ' + \
                 'where p3._Index_key = giv._Index_key and ' + \
                       'p3._Priority_key = vt._Term_key and ' + \
                       'vt._Vocab_key = 11 ' + \
                 'order by p3.new_gene desc, p3._Priority_key, giv.symbol', 'auto')

for r in results:
    if r['new_gene'] == 0:
        newGene = 'No'
    else:
        newGene = 'Yes'

    if r['E_annot'] == 0:
        eAnnot = 'No'
    else:
        eAnnot = 'Yes'

    fp.write(string.ljust(r['symbol'], 20))
    fp.write(SPACE)
    fp.write(string.ljust(newGene, 8))
    fp.write(SPACE)
    fp.write(string.ljust(r['term'], 10))
    fp.write(SPACE)
    fp.write(string.ljust(eAnnot, 4))
    fp.write(SPACE)
    fp.write(string.ljust(r['jnumID'], 10))
    fp.write(SPACE)
    fp.write(string.ljust(r['short_citation'], 255))
    fp.write(CRT)

fp.write('\n(%d rows affected)\n' % (len(results)))
reportlib.finish_nonps(fp)
