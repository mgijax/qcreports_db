#!/usr/local/bin/python

'''
#
# TR 4432/TR 4481
#
# Report:
#       Produce a report listing GXD specimens that have an age value that
#       is inappropriate for the anatomical structures attached to them.
#       Exclude TS28.
#       Display the following fields:
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
# lec   12/04/2007
#	- TR 8659; Stage 26 dpcMax has been corrected in the database, so no special changes are required
#
# lec   12/18/2006
#	- TR 8063; fixed logic; need to group by _Assay_key & _Specimen_key
#
# lec	04/06/2996
#	- converted regex to re
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
import os
import re
import string
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

fp = reportlib.init(sys.argv[0], 'GXD Specimens with incompatible Theiler stages and ages', os.environ['QCOUTPUTDIR'])

#
# insitu specimens with "embryonic day" age; exclude TS 28
#
db.sql('select s._Assay_key, s._Specimen_key, s.age, label = s.specimenLabel, t.stage, t.dpcMin, t.dpcMax ' + \
    'into #temp1 ' + \
    'from GXD_Specimen s, GXD_InSituResult r, GXD_ISResultStructure i, GXD_Structure c, GXD_TheilerStage t ' + \
    'where s._Specimen_key = r._Specimen_key and ' + \
          'r._Result_key = i._Result_key and ' + \
          'i._Structure_key = c._Structure_key and ' + \
          'c._Stage_key = t._Stage_key and ' + \
          's.age like "embryonic day%" ' + \
	  'and t.stage != 28 ', None)

#
# insitu specimens with "embryonic" age; include TS 28 for certain structures only
#
db.sql('insert into #temp1 ' + \
    'select s._Assay_key, s._Specimen_key, s.age, label = s.specimenLabel, t.stage, t.dpcMin, t.dpcMax ' + \
    'from GXD_Specimen s, GXD_InSituResult r, GXD_ISResultStructure i, GXD_Structure c, GXD_TheilerStage t ' + \
    'where s._Specimen_key = r._Specimen_key and ' + \
          'r._Result_key = i._Result_key and ' + \
          'i._Structure_key = c._Structure_key and ' + \
          'c._Stage_key = t._Stage_key and ' + \
          's.age like "embryonic%" ' + \
	  'and t.stage = 28 ' + \
	  'and not exists (select 1 from GXD_StructureName sn ' + \
	  'where c._Structure_key = sn._Structure_key and sn.structure in ("placenta", "decidua", "uterus"))', None)

#
# gel lanes with "embryonic day" age; no age ranges; exclude TS 28
#
db.sql('insert into #temp1 ' + \
    'select g._Assay_key, g._GelLane_key, g.age, label = g.laneLabel, t.stage, t.dpcMin, t.dpcMax ' + \
    'from GXD_GelLane g, GXD_GelLaneStructure l, GXD_Structure c, GXD_TheilerStage t ' + \
    'where g._GelLane_key = l._GelLane_key and ' + \
          'l._Structure_key = c._Structure_key and ' + \
          'c._Stage_key = t._Stage_key and ' + \
          'g.age like "embryonic day%" and ' + \
	  'g.age not like "%-%" ' + \
	  'and t.stage != 28 ', None)

#
# gel lanes with "embryonic day" age; no age ranges; include TS 28 for certain structures only
#
db.sql('insert into #temp1 ' + \
    'select g._Assay_key, g._GelLane_key, g.age, label = g.laneLabel, t.stage, t.dpcMin, t.dpcMax ' + \
    'from GXD_GelLane g, GXD_GelLaneStructure l, GXD_Structure c, GXD_TheilerStage t ' + \
    'where g._GelLane_key = l._GelLane_key and ' + \
          'l._Structure_key = c._Structure_key and ' + \
          'c._Stage_key = t._Stage_key and ' + \
          'g.age like "embryonic%" ' + \
	  'and g.age not like "%-%" ' + \
	  'and t.stage = 28 ' + \
	  'and not exists (select 1 from GXD_StructureName sn ' + \
	  'where c._Structure_key = sn._Structure_key and sn.structure in ("placenta", "decidua", "uterus"))', None)

#
# select specimens/gel lanes and group by assay & specimen
# take the mininum stage dpc value and maximum stage dpc value from all structures annotated to 
# a particular specimen/gel lane
#
# we want to make sure the "age" is within the dpc range based on *all* annotated structures of a given
# specimen label/gel lane.
#
# for example:  if a lane has "embryonic day 0.5,22" and structures from Stage 1 and Stage 28,
# then dpcMin = dpcMin from Stage 1
# then dpcMax = dpcMax from Stage 28
# so the age values (0.5 and 22) for this specimen must be between 0.0 and 1500.00
#

db.sql('select distinct * into #temp2 from #temp1', None)
db.sql('create index idx1 on #temp2(_Assay_key)', None)
db.sql('create index idx2 on #temp2(_Specimen_key)', None)
db.sql('select t._Assay_key, t.age, t.label, t.stage, dpcMin = min(t.dpcMin), dpcMax = max(t.dpcMax) ' + \
	'into #temp3 ' + \
	'from #temp2 t ' + \
	'group by t._Assay_key, t._Specimen_key ', None)
db.sql('create index idx1 on #temp3(_Assay_key)', None)

##

results = db.sql('select distinct t._Assay_key, t.age, t.label, t.stage, t.dpcMin, t.dpcMax, ' + \
	'a1.accID "MGI", a2.accID "J"' + \
    'from #temp3 t, GXD_Assay a, ACC_Accession a1, ACC_Accession a2 ' + \
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
	  'a2.preferred = 1 ' + \
    'order by a1.accID', 'auto')

s = ''
count = 0

for r in results:

    stage = r['stage']

    age = r['age']
    m = re.search('[0-9]',age)

    # if age has no numeric specified, print it out; probable error

    if m == None:
       	s = s + r['MGI'] + TAB + r['J'] + TAB + mgi_utils.prvalue(r['label']) + CRT
       	count = count + 1
       	continue

    start = m.start()
    range = age[start:]

    # parse by range "-" or list ","

    m = re.search('[-,]', range)

    if m == None:
       	minAge = string.atof(range)
       	maxAge = minAge
    else:
        delim = m.start()
       	minAge = string.atof(range[0:delim])
       	maxAge = string.atof(range[delim+1:])
	
    dpcMin = r['dpcMin']
    dpcMax = r['dpcMax']

    # if the age min is below the dpc min or age max is above the dpc max, print

    if (minAge < dpcMin or maxAge > dpcMax):
       	s = s + r['MGI'] + TAB + r['J'] + TAB + mgi_utils.prvalue(r['label']) + CRT
       	count = count + 1

fp.write(CRT + 'Number of specimens: ' + str(count) + 2*CRT)
fp.write(s)

reportlib.finish_nonps(fp)
