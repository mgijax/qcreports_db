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
# lec	10/27/2014
#	- add 'stage' to output so user can clearly see "duplicate" entries
#
# lec	03/11/2014
#	- TR11597/sort by mgiID desc
#
# sc 	
#	- TR11543; Updated GXD_TheilerStage to TS27 dpcMin=21.01, dpcMax=24.0; TS28 dpcMin=21.01
#
# lec	09/08/2010
#	- TR 10344; exclude J:153498/Eurexpress
#
# lec	05/19/2010
#	- TR 10204; add "decidua basalis" and "decidua capsularis"
#
# lec	05/01/2008
#	- TR 8775; on select GXD assay types
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
import string
import re
import mgi_utils
import reportlib

try:
    if os.environ['DB_TYPE'] == 'postgres':
        import pg_db
        db = pg_db
        db.setTrace()
        db.setAutoTranslateBE()
    else:
        import db
except:
    import db


CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fp = reportlib.init(sys.argv[0], 'GXD Specimens and Gel Lanes with incompatible Theiler stages and ages', os.environ['QCOUTPUTDIR'])

fp.write('1. insitu specimens with "embryonic day" age; exclude TS 28\n')
fp.write('2. insitu specimens with "embryonic" age; include TS 28 for certain structures only\n')
fp.write('   (placenta, decidua, decidua basalis, decidua capsularis, uterus)\n')
fp.write('3. gel lanes with "embryonic day" age; no age ranges; exclude TS 28\n')
fp.write('4. gel lanes with "embryonic day" age; no age ranges; include TS 28 for certain structures only\n')
fp.write('   (placenta, decidua, decidua basalis, decidua capsularis, uterus)\n')
fp.write('5. excludes J:153498/Eurexpress\n\n')

fp.write('select specimens/gel lanes and group by assay & specimen\n')
fp.write('take the mininum stage dpc value and maximum stage dpc value from all structures annotated to \n')
fp.write('a particular specimen/gel lane\n\n')

fp.write('we want to make sure the "age" is within the dpc range based on *all* annotated structures of a given\n')
fp.write('specimen label/gel lane.\n\n')

fp.write('for example:  if a lane has "embryonic day 0.5,22" and structures from Stage 1 and Stage 28,\n')
fp.write('then dpcMin = dpcMin from Stage 1\n')
fp.write('then dpcMax = dpcMax from Stage 28\n')
fp.write('so the age values (0.5 and 22) for this specimen must be between 0.0 and 1500.00\n')

#
#
# insitu specimens with "embryonic day" age; exclude TS 28
#
db.sql('''
    select s._Assay_key, s._Specimen_key, s.age, 
	   s.specimenLabel as label, 
	   t.stage, t.dpcMin, t.dpcMax 
    into #temp1 
    from GXD_Assay a, GXD_Specimen s, GXD_InSituResult r, 
	 GXD_ISResultStructure i, GXD_Structure c, GXD_TheilerStage t 
    where a._AssayType_key in (1,2,3,4,5,6,8,9) and 
	  a._Refs_key not in (154591) and 
	  a._Assay_key = s._Assay_key and 
	  s._Specimen_key = r._Specimen_key and 
          r._Result_key = i._Result_key and 
          i._Structure_key = c._Structure_key and 
          c._Stage_key = t._Stage_key and 
          s.age like 'embryonic day%' and 
	  t.stage != 28 
	''', None)

#
# insitu specimens with "embryonic" age; include TS 28 for certain structures only
#
db.sql('''
    insert into #temp1 
    select s._Assay_key, s._Specimen_key, s.age, 
	   s.specimenLabel as label, 
	   t.stage, t.dpcMin, t.dpcMax 
    from GXD_Assay a, GXD_Specimen s, GXD_InSituResult r, 
	 GXD_ISResultStructure i, GXD_Structure c, GXD_TheilerStage t 
    where a._AssayType_key in (1,2,3,4,5,6,8,9) and 
	  a._Refs_key not in (154591) and 
	  a._Assay_key = s._Assay_key and 
          s._Specimen_key = r._Specimen_key and 
          r._Result_key = i._Result_key and 
          i._Structure_key = c._Structure_key and 
          c._Stage_key = t._Stage_key and 
          s.age like 'embryonic%' 
	  and t.stage = 28 
	  and not exists (select 1 from GXD_StructureName sn 
	  where c._Structure_key = sn._Structure_key 
	  and sn.structure in ('placenta', 'decidua', 'decidua basalis', 'decidua capsularis', 'uterus'))
	''', None)

#
# gel lanes with "embryonic day" age; no age ranges; exclude TS 28
#
db.sql('''
    insert into #temp1 
    select g._Assay_key, g._GelLane_key, g.age, 
	   g.laneLabel as label, 
	   t.stage, t.dpcMin, t.dpcMax 
    from GXD_Assay a, GXD_GelLane g, GXD_GelLaneStructure l, 
	 GXD_Structure c, GXD_TheilerStage t 
    where a._Refs_key not in (154591) and 
	  a._Assay_key = g._Assay_key and 
          g._GelLane_key = l._GelLane_key and 
          l._Structure_key = c._Structure_key and 
          c._Stage_key = t._Stage_key and 
          g.age like 'embryonic day%' and 
	  g.age not like '%-%' 
	  and t.stage != 28 
	''', None)

#
# gel lanes with "embryonic day" age; no age ranges; include TS 28 for certain structures only
#
db.sql('''
    insert into #temp1 
    select g._Assay_key, g._GelLane_key, g.age, 
	   g.laneLabel as label, t.stage, t.dpcMin, t.dpcMax 
    from GXD_Assay a, GXD_GelLane g, GXD_GelLaneStructure l, GXD_Structure c, GXD_TheilerStage t 
    where a._Refs_key not in (154591) and 
	  a._Assay_key = g._Assay_key and 
          g._GelLane_key = l._GelLane_key and 
          l._Structure_key = c._Structure_key and 
          c._Stage_key = t._Stage_key and 
          g.age like 'embryonic%' 
	  and g.age not like '%-%' 
	  and t.stage = 28 
	  and not exists (select 1 from GXD_StructureName sn 
	  where c._Structure_key = sn._Structure_key 
	  and sn.structure in ('placenta', 'decidua', 'decidua basalis', 'decidua capsularis', 'uterus'))
	''', None)

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
db.sql('create index temp2_idx1 on #temp2(_Assay_key)', None)
db.sql('create index temp2_idx2 on #temp2(_Specimen_key)', None)
db.sql('''
	select distinct t._Assay_key, t.age, t.label, t.stage, 
		  min(t.dpcMin) as dpcMin, 
		  max(t.dpcMax) as dpcMax
	into #temp3 
	from #temp2 t 
	group by t._Assay_key, t._Specimen_key, t.age, t.label, t.stage
	''', None)
db.sql('create index temp3_idx on #temp3(_Assay_key)', None)

##

results = db.sql('''
	select distinct t.age, t.label, t.stage, t.dpcMin, t.dpcMax, 
	                a1.accID as mgi, a2.accID as jnum
        from #temp3 t, GXD_Assay a, ACC_Accession a1, ACC_Accession a2 
        where t._Assay_key = a._Assay_key and 
	  a._Assay_key = a1._Object_key and 
          a1._MGIType_key = 8 and 
          a1._LogicalDB_key = 1 and 
          a1.prefixPart = 'MGI:' and 
          a1.preferred = 1 and 
          a._Refs_key = a2._Object_key and 
          a2._MGIType_key = 1 and 
          a2._LogicalDB_key = 1 and 
          a2.prefixPart = 'J:' and 
	  a2.preferred = 1 
    	order by a1.accID desc
    	''', 'auto')

s = ''
count = 0

for r in results:

    age = r['age']
    m = re.search('[0-9]',age)

    # if age has no numeric specified, print it out; probable error

    if m == None:
       	s = s + r['mgi'] + TAB + r['jnum'] + TAB + mgi_utils.prvalue(r['label']) + CRT
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
       	s = s + r['mgi'] + TAB + r['jnum'] + TAB + mgi_utils.prvalue(r['label']) + TAB + str(r['stage']) + CRT
       	count = count + 1

fp.write(CRT + 'Number of specimens: ' + str(count) + 2*CRT)
fp.write(s)

reportlib.finish_nonps(fp)
