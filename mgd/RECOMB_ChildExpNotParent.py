#!/usr/local/bin/python

'''
#
# TR 8775: TR 8618
#
# Report:
#
# List anatomical structures used in assays that have been annotated as having
# no expression, but the children used in the same assay have been annotated
# as having expression.
#
# Columns to display:
#    1) J-Number of the assay
#    2) MGI ID of the assay
#    3) Stage of the structures in question
#    4) Parent structure (with absent annotation)
#    5) Child structure(s) (separated by a '|' if more than one)
# 
# Order by MGI ID, stage AND parent structure.
# 
# Originally requested as a custom SQL (TR 8073).
#
# Usage:
#       RECOMB_ChildExpNotParent.py
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
import string
import reportlib
import db

db.setTrace()
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Create the report file AND write the heading to it.
#
fp = reportlib.init(sys.argv[0], 'Assays in which a parent structure is annotated as having no expression while its children have expression.', outputdir = os.environ['QCOUTPUTDIR'])
fp.write(2*CRT)
fp.write(string.ljust('J-Number', 12))
fp.write(SPACE)
fp.write(string.ljust('MGI ID', 12))
fp.write(SPACE)
fp.write(string.ljust('Stage', 5))
fp.write(SPACE)
fp.write(string.ljust('Parent Structure', 80))
fp.write(SPACE)
fp.write(string.ljust('Child Structure(s)', 100))
fp.write(CRT)
fp.write(12*'-')
fp.write(SPACE)
fp.write(12*'-')
fp.write(SPACE)
fp.write(5*'-')
fp.write(SPACE)
fp.write(80*'-')
fp.write(SPACE)
fp.write(100*'-')
fp.write(CRT)

#
# Identify all cases where the parent structure has no expression, but has
# a child that does have expression (strength > 1).
#
db.sql('''
	SELECT r._Specimen_key, 
                   s._Structure_key as parentStructureKey, 
                   s2._Structure_key as childStructureKey 
            INTO work 
            FROM GXD_InSituResult r, GXD_InSituResult r2, 
                 GXD_ISResultStructure s, GXD_ISResultStructure s2, 
                 GXD_StructureClosure c, GXD_Specimen sp, 
                 GXD_Specimen sp2, GXD_Assay a, GXD_Assay a2 
            WHERE r._Strength_key = 1 
                  AND r._Result_key = s._Result_key 
                  AND r._Specimen_key = sp._Specimen_key 
		  AND sp._Assay_key = a._Assay_key 
		  AND a._AssayType_key in (10,11) 
                  AND r2._Strength_key > 1 
                  AND r2._Result_key = s2._Result_key 
                  AND r2._Specimen_key = sp2._Specimen_key 
                  AND sp._Assay_key = sp2._Assay_key 
                  AND sp2._Assay_key = a2._Assay_key 
		  AND a2._AssayType_key in (10,11) 
                  AND sp._Genotype_key = sp2._Genotype_key 
                  AND sp.age = sp2.age 
                  AND s._Structure_key = c._Structure_key 
                  AND s2._Structure_key = c._Descendent_key
	''', None)

#
# Get all of the results for the report.  This needs to be ordered by
# MGI ID, stage AND parent structure in order to get the records to be
# grouped properly AND merge all of the child structures that share these
# other fields in common.
#
results = db.sql('''
	SELECT distinct j.accID as JNumber, 
                   a.accID as MGIID, 
                   d._Stage_key, 
                   d.printName as parentStructure, 
                   d2.printName as childStructure 
            FROM work w, GXD_Specimen s, GXD_Expression e, 
                 ACC_Accession a, ACC_Accession j, 
                 GXD_Structure d, GXD_Structure d2 
            WHERE w._Specimen_key = s._Specimen_key 
                  AND s._Assay_key = e._Assay_key 
		  AND e.isForGXD = 0 
                  AND e.expressed = 1 
                  AND s._Assay_key = a._Object_key 
                  AND a._MGIType_key = 8 
                  AND e._Refs_key = j._Object_key 
                  AND j._MGIType_key = 1 
                  AND j.prefixPart = 'J:' 
                  AND w.parentStructureKey = d._Structure_key 
                  AND w.childStructureKey = d2._Structure_key 
            ORDER BY a.accID, d._Stage_key, d.printName
	''', 'auto')

#
# Initialize the "Last" variables that keep track of the last value for
# each field of the report.  These are used to determine when to write the
# next record to the report (when certain fields change) AND also hold
# the actual strings to write.
#
jNumberLast = ''
mgiIDLast = ''
stageLast = ''
parentStructureLast = ''
childStructureList = ''

#
# Process each row of the results set.
#
rows = 0
for r in results:

    #
    # Save the fields from the new row of the results set.
    #
    jNumber = r['JNumber']
    mgiID = r['MGIID']
    stage = str(r['_Stage_key'])
    parentStructure = r['parentStructure']
    childStructure = r['childStructure']

    #
    # If the MGI ID, stage or parent structure is different than the last
    # row, write the last set of data to the report.  This does not happen
    # if this is the first row of the results set.
    #
    if mgiID != mgiIDLast or stage != stageLast or parentStructure != parentStructureLast:
        if mgiIDLast != '':
            fp.write(string.ljust(jNumberLast, 12))
            fp.write(SPACE)
            fp.write(string.ljust(mgiIDLast, 12))
            fp.write(SPACE)
            fp.write(string.ljust(stageLast, 5))
            fp.write(SPACE)
            fp.write(string.ljust(parentStructureLast, 80))
            fp.write(SPACE)
            fp.write(string.ljust(childStructureList, 100))
            fp.write(CRT)

            #
            # Clear the child structure list AND prepare to build a new one
            # for the next MGI ID, stage AND parent structure.
            #
            childStructureList = ''
	    rows = rows + 1

    #
    # Save the new fields as the "Last" fields.
    #
    jNumberLast = jNumber
    mgiIDLast = mgiID
    stageLast = stage
    parentStructureLast = parentStructure

    #
    # Append the child structure to the '|' delimited list of child structures
    # for this MGI ID, stage AND parent structure combination.
    #
    if childStructureList == '':
        childStructureList = childStructure
    else:
        childStructureList = childStructureList + '|' + childStructure

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
fp.write(string.ljust(parentStructureLast, 80))
fp.write(SPACE)
fp.write(string.ljust(childStructureList, 100))
fp.write(CRT)
rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))

reportlib.finish_nonps(fp)
