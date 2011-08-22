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
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

# The list of journals; one report for the set of papers within each sub list
journals = [ ['Dev Biol', 'Development'], ['Dev Dyn'], ['Mech Dev'], ['Gene Expr Patterns', 'Brain Res Gene Expr Patterns'] ]

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
	fp.write(CRT)
	fp.write(string.ljust('-----', 30))
	fp.write(SPACE)
	fp.write(string.ljust('-----------', 12))
	fp.write(SPACE)
	fp.write(string.ljust('-----------', 12))
	fp.write(SPACE)
	fp.write(string.ljust('---------', 20))
	fp.write(CRT)

	# get set of references not coded with high priority

	db.sql('''
	       select distinct i._Refs_key, i._Marker_key, conditional = t.term 
	       into #markers1 
	       from GXD_Index i, BIB_Refs b, VOC_Term t 
	       where i._Refs_key = b._Refs_key 
	       and b.journal in ("%s")
	       and i._Priority_key = 74714 /* high */ 
	       and i._ConditionalMutants_key = t._Term_key 
	       and not exists (select 1 from GXD_Assay a 
	       where i._Refs_key = a._Refs_key)
	       ''' % journalTitle, None)

	db.sql('create index idx1 on #markers1(_Refs_key)', None)
	db.sql('select m.*, markerCount = count(*) into #mcount1 from #markers1 m group by _Refs_key', None)
	db.sql('create index idx1 on #mcount1(_Refs_key)', None)

	# get the set of references not coded with high priority,
	# add newGeneCount column to be updated later

	results = db.sql('select distinct a.accID, i._Refs_key, i.markerCount, i.conditional, newGeneCount = 0 ' + \
			 'into #final ' + \
			 'from #mcount1 i, ACC_Accession a ' + \
			 'where i._Refs_key = a._Object_key ' + \
			 'and a._MGIType_key = 1 ' + \
			 'and a.prefixPart = "J:"', None)

	#
	# new genes
	#
	# the set of references/markers = high priorty
	# and references/markers are not referenced in the assay module
	#

	db.sql('''
	       select distinct i._Refs_key, i._Marker_key 
	       into #markers2 
	       from GXD_Index i, BIB_Refs b 
	       where i._Refs_key = b._Refs_key 
	       and b.journal in ("%s")
	       and i._Priority_key = 74714 /* high */
	       and not exists (select 1 from GXD_Assay a where i._Refs_key = a._Refs_key) 
	       and not exists (select 1 from GXD_Assay a where i._Marker_key = a._Marker_key) 
	       ''' % journalTitle, None)
	db.sql('create index idx1 on #markers2(_Refs_key)', None)

	#
	# by reference, get the count
	#
	db.sql('select m.*, newGeneCount = count(*) into #mcount2 from #markers2 m group by _Refs_key', None)
	db.sql('create index idx1 on #mcount2(_Refs_key)', None)

	#
	# by reference, set #final.newGeneCount = #mcount2.newGeneCount
	#
	db.sql('''
	       update #final 
	       set newGeneCount = m.newGeneCount
	       from #final f, #mcount2 m
	       where f._Refs_key = m._Refs_key
	       ''', None)

	# now write the report
	results = db.sql('select * from #final order by newGeneCount desc, markerCount desc', 'auto')

	for r in results:
	    fp.write(string.ljust(str(r['accID']), 30))
	    fp.write(SPACE)
	    fp.write(string.ljust(str(r['markerCount']), 12))
	    fp.write(SPACE)
	    fp.write(string.ljust(str(r['newGeneCount']), 12))
	    fp.write(SPACE)
	    fp.write(string.ljust(str(r['conditional']), 20))
	    fp.write(CRT)

	fp.write('%s(%d rows affected)%s%s' % (CRT, len(results), CRT, CRT))

	# drop all the temp tables because we are looping
        db.sql('drop table #markers1', None)
	db.sql('drop table #mcount1', None)
	db.sql('drop table #final', None)
	db.sql('drop table #markers2', None)
        db.sql('drop table #mcount2', None)

    reportlib.finish_nonps(fp)

#
# Main
#

for jList in journals:
    fileName = 'GXD_' + string.replace(string.join(jList, 'and '), ' ', '')
    processJournal(jList, fileName)

