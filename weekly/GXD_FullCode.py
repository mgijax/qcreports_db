#!/usr/local/bin/python

'''
#
# TR 6469
#
# Report:
#
# Papers to full code by specific Journals
#
# Usage:
#       GXD_FullCode.py
#
# Notes:
#
# History:
#
# lec   10/24/2014
#       - TR11750/postres complient
#
# lec	12/24/2012
#	- TR11206/re-open Dev Biol and Development and Dev Dyn
#
# lec	06/11/2012
#	- TR11105/retire Dev Biol and Development
#
# lec	09/23/2009
#	- TR 9806/add "Conditional" column
#	  change "new" gene definition
#
# sc   07/09/2007
#      -TR8349; combined Dev Biol and Development into one report
#	        combined Gene Expr Patterns and Brain Res Gene Expr Patterns 
#                  into one report
#               added papers not coded with new markers as third column
#                  instead of separate listing 	        
#
# lec	02/09/2007
#	- TR 8147; added Proc Natl Acad Sci U S A
#
# lec	01/12/2005
#	- converted GXD_DevBiol.sql, GXD_Development.sql, GXD_MechDev.sql, GXD_GeneExprPatterns.sql to one report
#	- added Dev Dyn
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

# The list of journals; one report for the set of papers within each sub list
journals = [ ['Mech Dev'], ['Gene Expr Patterns', 'Brain Res Gene Expr Patterns' ] , ['Dev Biol'], ['Development'], ['Dev Dyn'] ]

def processJournal(jList, fileName):

    fp = reportlib.init(fileName, outputdir = os.environ['QCOUTPUTDIR'], printHeading = "DBINFO")

    for journalTitle in jList:

	fp.write('Reference and Number of Markers Analyzed for Journal: %s' % (journalTitle) + 2*CRT)
	fp.write(string.ljust('accID', 30))
	fp.write(SPACE)
	fp.write(string.ljust('markerCount', 12))
	fp.write(SPACE)
	fp.write(string.ljust('newGeneCount', 12))
	fp.write(SPACE)
	fp.write(string.ljust('Conditional', 20))
	fp.write(SPACE)
	fp.write(string.ljust('Priorty', 10))
	fp.write(SPACE)
	fp.write(string.ljust('Short Citation', 20))
	fp.write(CRT)
	fp.write(string.ljust('-----', 30))
	fp.write(SPACE)
	fp.write(string.ljust('-----------', 12))
	fp.write(SPACE)
	fp.write(string.ljust('-----------', 12))
	fp.write(SPACE)
	fp.write(string.ljust('---------', 20))
	fp.write(SPACE)
	fp.write(string.ljust('---------', 10))
	fp.write(SPACE)
	fp.write(string.ljust('---------', 20))
	fp.write(CRT)

	# get set of references not coded with high/medium priority

	db.sql('''
	       select distinct i._Refs_key, i._Marker_key, 
                               t1.term as conditional,
                               t2.term as priority
	       into temporary table markers1 
	       from GXD_Index i, BIB_Refs b, VOC_Term t1, VOC_Term t2
	       where i._Refs_key = b._Refs_key 
	       and b.journal in ('%s')
	       and i._Priority_key in (74714, 74715) /* high/medium */
	       and i._Priority_key = t2._Term_key 
	       and i._ConditionalMutants_key = t1._Term_key 
	       and not exists (select 1 from GXD_Assay a 
	       where i._Refs_key = a._Refs_key)
	       ''' % journalTitle, None)

	db.sql('create index markers1_idx1 on markers1(_Refs_key)', None)

	db.sql('''WITH ref_counts1 AS (
		SELECT _Refs_key, count(*) AS markerCount
		FROM markers1
		GROUP BY _Refs_key
		)
		select m.*, r.markerCount
		into mcount1 
		from markers1 m , ref_counts1 r
		where m._Refs_key = r._Refs_key
		''', None)

	db.sql('create index mcount1_idx1 on mcount1(_Refs_key)', None)

	# get the set of references not coded with high priority,
	# add newGeneCount column to be updated later

	results = db.sql('''
		select distinct a.jnumID, i._Refs_key, i.markerCount, 
                                i.conditional, i.priority, 
                                a.short_citation,
                                0 as newGeneCount
		into temporary table final 
		from mcount1 i, BIB_Citation_Cache a 
		where i._Refs_key = a._Refs_key 
		''', None)

	#
	# new genes
	#
	# the set of references/markers = high/medium priorty
	# and references/markers are not referenced in the assay module
	#

	db.sql('''
	       select distinct i._Refs_key, i._Marker_key
	       into temporary table markers2 
	       from GXD_Index i, BIB_Refs b
	       where i._Refs_key = b._Refs_key 
	       and b.journal in ('%s')
	       and i._Priority_key in (74714, 74715) /* high/medium */
	       and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key) 
	       and not exists (select 1 from GXD_Assay a where i._Marker_key = a._Marker_key) 
	       ''' % journalTitle, None)
	db.sql('create index markers2_idx1 on markers2(_Refs_key)', None)

	#
	# by reference, get the count
	#
	db.sql('''WITH ref_counts2 AS (
		SELECT _Refs_key, count(*) AS newGeneCount
		FROM markers2
		GROUP BY _Refs_key
		)
		select m.*, r.newGeneCount
		into mcount2
		from markers2 m , ref_counts2 r
		where m._Refs_key = r._Refs_key
		''', None)

	db.sql('create index mcount2_idx1 on mcount2(_Refs_key)', None)

	#
	# by reference, set final.newGeneCount = mcount2.newGeneCount
	#
	db.sql('''
	       update final 
	       set newGeneCount = m.newGeneCount
	       from mcount2 m
	       where final._Refs_key = m._Refs_key
	       ''', None)

	# now write the report
	results = db.sql('select * from final order by priority, newGeneCount desc, markerCount desc', 'auto')

	for r in results:
	    fp.write(string.ljust(str(r['jnumID']), 30))
	    fp.write(SPACE)
	    fp.write(string.ljust(str(r['markerCount']), 12))
	    fp.write(SPACE)
	    fp.write(string.ljust(str(r['newGeneCount']), 12))
	    fp.write(SPACE)
	    fp.write(string.ljust(str(r['conditional']), 20))
	    fp.write(SPACE)
	    fp.write(string.ljust(str(r['priority']), 10))
	    fp.write(SPACE)
	    fp.write(string.ljust(str(r['short_citation']), 50))
	    fp.write(CRT)

	fp.write('%s(%d rows affected)%s%s' % (CRT, len(results), CRT, CRT))

	# drop all the temp tables because we are looping
        db.sql('drop table markers1', None)
	db.sql('drop table mcount1', None)
	db.sql('drop table final', None)
	db.sql('drop table markers2', None)
        db.sql('drop table mcount2', None)

    reportlib.finish_nonps(fp)

#
# Main
#

for jList in journals:
    fileName = 'GXD_' + string.replace(string.join(jList, 'and '), ' ', '')
    processJournal(jList, fileName)

