#!/usr/local/bin/python

'''
#
# TR 8618
#
# Report:
#
# List anatomical structures used in assays that have been annotated as having
# no expression, but the children used in the same assay have been annotated
# as having expression.
#
# Exclude J:80501, J:80502, J:91257, J:93300, J:101679, J:122989
#
# Columns to display:
#    1) J-Number of the assay
#    2) MGI ID of the assay
#    3) Stage of the structures in question
#    4) Parent structure (with absent annotation)
#    5) Child structure(s) (separated by a '|' if more than one)
# 
# Order by MGI ID, stage and parent structure.
# 
# Originally requested as a custom SQL (TR 8073).
#
# Usage:
#       GXD_ChildExpNotParent.py
#
# Notes:
#
# History:
#
# lec   03/11/2014
#       - TR11597/sort by mgiID desc
#
# lec	05/01/2008
#	- TR 8775; on select GXD assay types
#
# dbm	11/28/2007
#	- new
#
'''

import sys
import os
import string
import reportlib
import db

#db.setTrace()
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

excluded = "'J:80501','J:80502','J:91257','J:93300','J:101679','J:122989'"

fp = reportlib.init(sys.argv[0], 'Assays in which a parent structure is annotated as having no expression while its children have expression.', outputdir = os.environ['QCOUTPUTDIR'])

fp.write(CRT)
fp.write('Excluded J-Numbers: J:80501, J:80502, J:91257, J:93300, J:101679, J:122989')

fp.write(2*CRT)

#
# Identify all cases where the parent structure has no expression, but has
# a child that does have expression (strength > 1).
#

db.sql('''
	SELECT a._Assay_key,
	       r._Specimen_key, 
               s._EMAPA_Term_key as parentKey, 
	       s._Stage_key,
               s2._EMAPA_Term_key as childKey
        INTO TEMPORARY TABLE work 
        FROM GXD_InSituResult r, GXD_InSituResult r2, 
             GXD_ISResultStructure s, GXD_ISResultStructure s2, 
	     GXD_Specimen sp, GXD_Specimen sp2,
             GXD_Assay a, GXD_Assay a2,
             DAG_Closure c
        WHERE r._Strength_key = 1 
              and r._Result_key = s._Result_key 
              and r._Specimen_key = sp._Specimen_key 
	      and sp._Assay_key = a._Assay_key 
	      and a._AssayType_key in (1,2,3,4,5,6,8,9) 
              and r2._Strength_key > 1 
              and r2._Result_key = s2._Result_key 
              and r2._Specimen_key = sp2._Specimen_key 
              and sp._Assay_key = sp2._Assay_key 
              and sp2._Assay_key = a2._Assay_key 
	      and a2._AssayType_key in (1,2,3,4,5,6,8,9) 
              and sp._Genotype_key = sp2._Genotype_key 
              and sp.age = sp2.age 
	      and s._Stage_key = s2._Stage_key
              and s._EMAPA_Term_key = c._AncestorObject_key
	      and c._MGIType_key = 13
              and s2._EMAPA_Term_key = c._DescendentObject_key
        UNION 
	SELECT a._Assay_key,
	       r._Specimen_key, 
               s._EMAPA_Term_key as parentKey, 
	       s._Stage_key,
               s2._EMAPA_Term_key as childKey
        FROM GXD_InSituResult r, GXD_InSituResult r2, 
             GXD_ISResultStructure s, GXD_ISResultStructure s2, 
	     GXD_Specimen sp, GXD_Specimen sp2,
             GXD_Assay a, GXD_Assay a2,
             VOC_TERM t
        WHERE r._Strength_key = 1 
              and r._Result_key = s._Result_key 
              and r._Specimen_key = sp._Specimen_key 
	      and sp._Assay_key = a._Assay_key 
	      and a._AssayType_key in (1,2,3,4,5,6,8,9) 
              and r2._Strength_key > 1 
              and r2._Result_key = s2._Result_key 
              and r2._Specimen_key = sp2._Specimen_key 
              and sp._Assay_key = sp2._Assay_key 
              and sp2._Assay_key = a2._Assay_key 
	      and a2._AssayType_key in (1,2,3,4,5,6,8,9) 
              and sp._Genotype_key = sp2._Genotype_key 
              and sp.age = sp2.age 
	      and s._Stage_key = s2._Stage_key
              and s._EMAPA_Term_key = t._Term_key
              and s2._EMAPA_Term_key = t._Term_key
	''', None)

db.sql('create index idx1 on work(_Specimen_key)', None)
db.sql('create index idx2 on work(parentKey)', None)
db.sql('create index idx3 on work(childKey)', None)

#
# Find distinct combinations of MGI ID, stage and parent structure to
# determine the number of rows that will be written to the report.
#
results = db.sql('''
	SELECT distinct a.accID, t.stage, d.term
        FROM work w, GXD_Expression e, 
             ACC_Accession a, ACC_Accession j, 
             VOC_Term d, VOC_Term d2, GXD_TheilerStage t
        WHERE e._Assay_key = w._Assay_key
	      and e._Specimen_key = w._Specimen_key 
	      and e.isForGXD = 1 
              and e.expressed = 1 
              and e._Assay_key = a._Object_key 
              and a._MGIType_key = 8 
              and e._Refs_key = j._Object_key 
              and j._MGIType_key = 1 
              and j.prefixPart = 'J:' 
              and j.accID not in (%s)
              and w.parentKey = d._Term_key 
              and w.childKey = d2._Term_key
	      and e._Stage_key = w._Stage_key
	      and e._Stage_key = t._Stage_key
	      --and j.accID in ('J:41321')
	''' % (excluded), 'auto')
fp.write('Row Count: ' + str(len(results)))

#
# Create the report file and write the heading to it.
#

fp.write(2*CRT)
fp.write(string.ljust('J-Number', 12))
fp.write(SPACE)
fp.write(string.ljust('MGI ID', 12))
fp.write(SPACE)
fp.write(string.ljust('Stage', 5))
fp.write(SPACE)
fp.write(string.ljust('Parent Structure', 50))
fp.write(SPACE)
fp.write(string.ljust('Child Structure(s)', 50))
fp.write(CRT)
fp.write(12*'-')
fp.write(SPACE)
fp.write(12*'-')
fp.write(SPACE)
fp.write(5*'-')
fp.write(SPACE)
fp.write(50*'-')
fp.write(SPACE)
fp.write(50*'-')
fp.write(CRT)

#
# Initialize the "Last" variables that keep track of the last value for
# each field of the report.  These are used to determine when to write the
# next record to the report (when certain fields change) and also hold
# the actual strings to write.
#
jNumberLast = ''
mgiIDLast = ''
stageLast = ''
parentLast = ''
childList = ''

#
#
# Get all of the results for the report.  This needs to be ordered by
# MGI ID, stage and parent structure in order to get the records to be
# grouped properly and merge all of the child structures that share these
# other fields in common.
#
results = db.sql('''
	SELECT distinct j.accID as jnum, 
               a.accID as mgiid, 
	       e._Stage_key,
               t.stage,
               d.term as parent, 
               d2.term as child 
        FROM work w, GXD_Expression e, 
             ACC_Accession a, ACC_Accession j, 
             VOC_Term d, VOC_Term d2, GXD_TheilerStage t
        WHERE e._Assay_key = w._Assay_key
	      and e._Specimen_key = w._Specimen_key 
	      and e.isForGXD = 1 
              and e.expressed = 1 
              and e._Assay_key = a._Object_key 
              and a._MGIType_key = 8 
	      and e._Stage_key = t._Stage_key
              and e._Refs_key = j._Object_key 
              and j._MGIType_key = 1 
              and j.prefixPart = 'J:' 
              and j.accID not in (%s)
              and w.parentKey = d._Term_key 
              and w.childKey = d2._Term_key 
	      and e._Stage_key = w._Stage_key
	      --and j.accID in ('J:41321')
        order by a.accID desc, e._Stage_key, d.term
	''' % (excluded), 'auto')

#
# Process each row of the results set.
#
for r in results:

    #
    # Save the fields from the new row of the results set.
    #
    jNumber = r['jnum']
    mgiID = r['mgiid']
    stage = str(r['stage'])
    parent = r['parent']
    child = r['child']

    #
    # If the MGI ID, stage, parent structure is different than the last
    # row, write the last set of data to the report.  This does not happen
    # if this is the first row of the results set.
    #
    if mgiID != mgiIDLast or stage != stageLast or parent != parentLast:
        if mgiIDLast != '':
            fp.write(string.ljust(jNumberLast, 12))
            fp.write(SPACE)
            fp.write(string.ljust(mgiIDLast, 12))
            fp.write(SPACE)
            fp.write(string.ljust(stageLast,5))
            fp.write(SPACE)
            fp.write(string.ljust(parentLast, 50))
            fp.write(SPACE)
            fp.write(string.ljust(childList, 50))
            fp.write(CRT)

            #
            # Clear the child structure list and prepare to build a new one
            # for the next MGI ID, stage and parent structure.
            #
            childList = ''

    #
    # Save the new fields as the "Last" fields.
    #
    jNumberLast = jNumber
    mgiIDLast = mgiID
    stageLast = stage
    parentLast = parent

    #
    # Append the child structure to the '|' delimited list of child structures
    # for this MGI ID, stage and parent structure combination.
    #
    if childList == '':
        childList = child
    else:
        childList = childList + '|' + child

#
# When there are no more rows in the results set, the last set of data still
# needs to be written to the report.
#
fp.write(string.ljust(jNumberLast, 12))
fp.write(SPACE)
fp.write(string.ljust(mgiIDLast, 12))
fp.write(SPACE)
fp.write(string.ljust(stageLast, 5))
fp.write(SPACE)
fp.write(string.ljust(parentLast, 50))
fp.write(SPACE)
fp.write(string.ljust(childList, 50))
fp.write(CRT)

reportlib.finish_nonps(fp)
