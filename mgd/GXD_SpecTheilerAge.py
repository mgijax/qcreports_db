#!/usr/local/bin/python

'''
#
# TR 4432/TR 4481
#
# Report:
#       Produce a report listing GXD specimens that have an age value that
#       is inappropriate for the anatomical structures attached to them.
#       Exclude TS28 and adjust the maximum range on TS26 to include ages
#       up to 19.9.  Display the following fields:
#
#       MGI ID (of the assay)  J Number  Specimen Label
#
#       Sort by the MGI ID
#
# Usage:
#       GXD_SpecTheilerAge.py
#
# Notes:
#
# History:
#
# lec	02/11/2003
#	- TR 4481; converted to QC report
#
# dbm   1/20/2003
#       - created
#
# dbm   1/28/2003
#       - added additional query against the GXD_GelLane table to include
#         results for assay type 'RT-PCR' in the report
#
'''

import sys
import string
import regex
import os
import db
import reportlib
import mgi_utils

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE


#
# Main
#

db.useOneConnection(1)
fp = reportlib.init(sys.argv[0], 'GXD Specimens with incompatible Theiler stages and ages', os.environ['QCREPORTOUTPUTDIR'])

cmds = []

cmds.append('select s._Assay_key, s.age, label = s.specimenLabel, t.stage, t.dpcMin, t.dpcMax ' + \
    'into #temp ' + \
    'from GXD_Specimen s, GXD_InSituResult r, GXD_ISResultStructure i, GXD_Structure c, GXD_TheilerStage t ' + \
    'where s._Specimen_key = r._Specimen_key and ' + \
          'r._Result_key = i._Result_key and ' + \
          'i._Structure_key = c._Structure_key and ' + \
          'c._Stage_key = t._Stage_key and ' + \
          's.age like "embryonic day%" ' + \
	  'and t.stage != 28 ' + \
    'union ' + \
    'select s._Assay_key, s.age, label = s.specimenLabel, t.stage, t.dpcMin, t.dpcMax ' + \
    'from GXD_Specimen s, GXD_InSituResult r, GXD_ISResultStructure i, GXD_Structure c, GXD_TheilerStage t ' + \
    'where s._Specimen_key = r._Specimen_key and ' + \
          'r._Result_key = i._Result_key and ' + \
          'i._Structure_key = c._Structure_key and ' + \
          'c._Stage_key = t._Stage_key and ' + \
          '(s.age like "embryonic%" or s.age = "perinatal") ' + \
	  'and t.stage = 28 ' + \
	  'and not exists (select 1 from GXD_StructureName sn ' + \
	  'where c._Structure_key = sn._Structure_key and sn.structure in ("placenta", "decidua", "uterus"))' + \
    'union ' + \
    'select g._Assay_key, g.age, label = g.laneLabel, t.stage, t.dpcMin, t.dpcMax ' + \
    'from GXD_GelLane g, GXD_GelLaneStructure l, GXD_Structure c, GXD_TheilerStage t ' + \
    'where g._GelLane_key = l._GelLane_key and ' + \
          'l._Structure_key = c._Structure_key and ' + \
          'c._Stage_key = t._Stage_key and ' + \
          'g.age like "embryonic day%" and ' + \
	  'g.age not like "%-%" ' + \
	  'and t.stage != 28 ' + \
    'union ' + \
    'select g._Assay_key, g.age, label = g.laneLabel, t.stage, t.dpcMin, t.dpcMax ' + \
    'from GXD_GelLane g, GXD_GelLaneStructure l, GXD_Structure c, GXD_TheilerStage t ' + \
    'where g._GelLane_key = l._GelLane_key and ' + \
          'l._Structure_key = c._Structure_key and ' + \
          'c._Stage_key = t._Stage_key and ' + \
          '(g.age like "embryonic%" or g.age = "perinatal") ' + \
	  'and g.age not like "%-%" ' + \
	  'and t.stage = 28 ' + \
	  'and not exists (select 1 from GXD_StructureName sn ' + \
	  'where c._Structure_key = sn._Structure_key and sn.structure in ("placenta", "decidua", "uterus"))')

cmds.append('create index idx1 on #temp(_Assay_key)')
db.sql(cmds, None)

##

results = db.sql('select distinct t.age, t.label, t.stage, t.dpcMin, t.dpcMax, a1.accID "MGI", a2.accID "J"' + \
    'from #temp t, GXD_Assay a, ACC_Accession a1, ACC_Accession a2 ' + \
    'where t._Assay_key = a._Assay_key and ' + \
	  'a._Assay_key = a1._Object_key and ' + \
          'a1._MGIType_key = 8 and ' + \
          'a1._LogicalDB_key = 1 and ' + \
          'a1.prefixPart = "MGI:" and ' + \
          'a1.preferred = 1 and ' + \
          'a._Refs_key = a2._Object_key and ' + \
          'a2._MGIType_key = 1 and ' + \
          'a2._LogicalDB_key = 1 and ' + \
          'a2.prefixPart = "J:" and ' + \
	  'a2.preferred = 1' + \
    'order by a1.accID', 'auto')

count = 0
for r in results:

    stage = r['stage']

    if stage == 28:

        fp.write(r['MGI'] + TAB + r['J'] + TAB + mgi_utils.prvalue(r['label']) + CRT)
       	count = count + 1
       	continue
    
    age = r['age']
    start = regex.search('[0-9]',age)

    if (start < 0):
       	fp.write(r['MGI'] + TAB + r['J'] + TAB + mgi_utils.prvalue(r['label']) + CRT)
       	count = count + 1
       	continue

    range = age[start:]
    delim = regex.search('[-,]',range)

    if (delim < 0):
       	minAge = string.atof(range)
       	maxAge = minAge
    else:
       	minAge = string.atof(range[0:delim])
       	maxAge = string.atof(range[delim+1:])
	
    dpcMin = r['dpcMin']
    dpcMax = r['dpcMax']

    # embryos which are Theiler Stage 27 are put in Theiler Stage 26
    if (stage == 26):
       	dpcMax = 19.9

    if (minAge < dpcMin or maxAge > dpcMax):
       	fp.write(r['MGI'] + TAB + r['J'] + TAB + mgi_utils.prvalue(r['label']) + CRT)
       	count = count + 1

fp.write(CRT + 'Number of specimens: ' + str(count) + CRT)

reportlib.finish_nonps(fp)
db.useOneConnection(0)
