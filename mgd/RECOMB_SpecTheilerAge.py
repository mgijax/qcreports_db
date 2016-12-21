#!/usr/local/bin/python

'''
#
# TR 8775: TR 4432/TR 4481
#
# Report:
#       Produce a report listing specimens that have an age value that
#       is inappropriate for the anatomical structures attached to them.
#       Exclude TS28.
#       Display the following fields:
#
#       MGI ID (of the assay)  J Number  Specimen Label
#
#       Sort by the MGI ID
#
# Usage:
#       RECOMB_SpecTheilerAge.py
#
# Notes:
#
# History:
#
# lec	05/01/2008
#	- new; TR 8775; copy from GXD
#
'''

import sys
import os
import re
import string
import mgi_utils
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fp = reportlib.init(sys.argv[0], '\nRecombinant/transgenic specimens with incompatible Theiler stages and ages', \
	os.environ['QCOUTPUTDIR'])

#
# insitu specimens with "embryonic day" age; exclude TS 27,28
#
db.sql('''
    select s._Assay_key, s._Specimen_key, s.age, s.specimenLabel as label, t.stage, t.dpcMin, t.dpcMax 
    into temporary table temp1 
    from GXD_Assay a, GXD_Specimen s, GXD_InSituResult r, 
	 GXD_ISResultStructure i, VOC_Term c, GXD_TheilerStage t 
    where a._AssayType_key in (10,11) and 
	  a._Assay_key = s._Assay_key and 
	  s._Specimen_key = r._Specimen_key and 
          r._Result_key = i._Result_key and 
          i._EMAPA_Term_key = c._Term_key and 
          i._Stage_key = t._Stage_key and 
          s.age like 'embryonic day%' 
	  and t.stage not in (27,28)
  ''', None)

#
# insitu specimens with "embryonic" age; include TS 28 for certain structures only
#
db.sql('''
    insert into temp1 
    select s._Assay_key, s._Specimen_key, s.age, s.specimenLabel as label, t.stage, t.dpcMin, t.dpcMax 
    from GXD_Assay a, GXD_Specimen s, GXD_InSituResult r, 
	 GXD_ISResultStructure i, VOC_Term c, GXD_TheilerStage t 
    where a._AssayType_key in (10,11) and 
	  a._Assay_key = s._Assay_key and 
          s._Specimen_key = r._Specimen_key and 
          r._Result_key = i._Result_key and 
          i._EMAPA_Term_key = c._Term_key and 
          i._Stage_key = t._Stage_key and 
          s.age like 'embryonic%' 
	  and t.stage = 28 
	  and c.term not in ('placenta', 'decidua', 'uterus')
    ''', None)

#
# select specimens and group by assay & specimen
# take the mininum stage dpc value and maximum stage dpc value from all structures annotated to 
# a particular specimen/gel lane
#
# we want to make sure the "age" is within the dpc range based on *all* annotated structures of a given
# specimen label.
#
# for example:  if a lane has "embryonic day 0.5,22" and structures from Stage 1 and Stage 28,
# then dpcMin = dpcMin from Stage 1
# then dpcMax = dpcMax from Stage 28
# so the age values (0.5 and 22) for this specimen must be between 0.0 and 1500.00
#

db.sql('select distinct * into temporary table temp2 from temp1', None)
db.sql('create index temp2_idx1 on temp2(_Assay_key)', None)
db.sql('create index temp2_idx2 on temp2(_Specimen_key)', None)
db.sql('''
	select t._Assay_key, t.age, t.label, t.stage, min(t.dpcMin) as dpcMin, max(t.dpcMax) as dpcMax 
	into temporary table temp3 
	from temp2 t 
	group by t._Assay_key, t._Specimen_key, t.age, t.label, t.stage, dpcMin, dpcMax
	''', None)
db.sql('create index temp3_idx1 on temp3(_Assay_key)', None)

##

results = db.sql('''
    select distinct t._Assay_key, t.age, t.label, t.stage, t.dpcMin, t.dpcMax, 
	a1.accID as mgi, a2.accID as jnum
    from temp3 t, GXD_Assay a, ACC_Accession a1, ACC_Accession a2 
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
    order by a1.accID
    ''', 'auto')

s = ''
count = 0

for r in results:

    stage = r['stage']

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
       	s = s + r['mgi'] + TAB + r['jnum'] + TAB + mgi_utils.prvalue(r['label']) + CRT
       	count = count + 1

fp.write('Number of specimens: ' + str(count) + 2*CRT)
fp.write(s)

reportlib.finish_nonps(fp)
