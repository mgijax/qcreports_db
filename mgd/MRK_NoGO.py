#!/usr/local/bin/python

'''
#
# MRK_NoGO.py 01/08/2002
#
# Report:
#       TR 3269 - Report 1
#
#	Report 1A
#	Title = Genes Not RIKEN or 'expressed' or 'EST' with no GO associations
#	Select markers of type 'gene' 
#		where 'current' name does not contain 'RIKEN' or 'expressed' or 'EST'
#               where the marker has no 'GO' association
#               where the reference count exludes J:23000, J:57747, J:63103, J:57656, J:51368, 
#               J:67225, J:67226, or any reference that has "Genbank Submission"  in 
#               the Journal title
#
#       Report in a tab delimited file with the following columns:
#
#    		MGI:ID
#    		symbol
#    		name
#    		number of references
#    		human or rat ortholog?    'yes'
#
#    	Report 1B
#    	Title = Genes Not RIKEN or 'expressed' or 'EST' with no GO associations
#    	Select markers of type 'gene'
#    		where 'current' name does not contain 'RIKEN' or 'expressed' or 'EST'
#               where the marker has no 'GO' association.
#
#    	Report in a tab delimited file with same columns as 1A
#
#	Report 1C
#	Title = Genes Not RIKEN or 'expressed' or 'EST' with no GO associations
#	Select markers of type 'gene' 
#		where 'current' name does not contain 'RIKEN' or 'expressed' or 'EST'
#               where the marker has no 'GO' association
#               where the reference count includes J:23000, J:57747, J:63103, J:57656, J:51368, 
#               J:67225, J:67226, or any reference that has "Genbank Submission"  in 
#               the Journal title
#
#    	Report in a tab delimited file with same columns as 1A
#
#	TR 4491
#	Report 1D
#	Title = Genes Not RIKEN or 'expressed' or 'EST' with no GO associations
#    	Select markers of type 'gene'
#    		where 'current' name does not contain 'RIKEN' or 'expressed' or 'EST'
#               where the marker has no 'GO' association.
#
#	Report in a tab delimited file with the following columns:
#
#	J: of reference associated with the Marker, selected for GO but has not been used in annotation
#	MGI:ID
#	symbol
#	name
#
# Usage:
#       MRK_NoGO.py
#
# Notes:
#	- all reports use mgireport directory for output file
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
#
# lec	02/11/2003
#	- TR 4491; added Report 1D
#
# lec	01/08/2002
#	- created
#
'''
 
import sys 
import os
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

def writeRecord(fp, r):

	fp.write(r['mgiID'] + TAB + \
	         r['symbol'] + TAB + \
	         r['name'] + TAB + \
	         `r['numRefs']` + TAB)

	if hasHomology.has_key(r['_Marker_key']):
		fp.write('yes' + CRT)
	else:
		fp.write('no' + CRT)

def writeRecordD(fp, r):

	fp.write(r['jnumID'] + TAB + \
	         r['mgiID'] + TAB + \
	         r['symbol'] + TAB + \
	         r['name'] + CRT)

#
# Main
#

fpA = reportlib.init("MRK_NoGO_A", printHeading = 0, outputdir = os.environ['QCREPORTOUTPUTDIR'])
fpB = reportlib.init("MRK_NoGO_B", printHeading = 0, outputdir = os.environ['QCREPORTOUTPUTDIR'])
fpC = reportlib.init("MRK_NoGO_C", printHeading = 0, outputdir = os.environ['QCREPORTOUTPUTDIR'])
fpD = reportlib.init("MRK_NoGO_D", printHeading = 0, outputdir = os.environ['QCREPORTOUTPUTDIR'])

cmds = []

cmds.append('select m._Marker_key, m.symbol, m.name, mgiID = a.accID, a.numericPart ' + \
'into #markers ' + \
'from MRK_Marker m, MRK_Acc_View a ' + \
'where m._Marker_Type_key = 1 ' + \
'and m._Marker_Status_key = 1 ' + \
'and m.name not like "%RIKEN%" ' + \
'and m.name not like "%expressed%" ' + \
'and m.name not like "EST %" ' + \
'and m._Marker_key = a._Object_key ' + \
'and a._LogicalDB_key = 1 ' + \
'and a.prefixPart = "MGI:" ' + \
'and a.preferred = 1 ' + \
'and not exists (select 1 from  VOC_Annot a ' + \
'where m._Marker_key = a._Object_key ' + \
'and a._AnnotType_key = 1000 ) ')

cmds.append('select distinct m._Marker_key ' + \
'from #markers m ' + \
'where exists (select 1 from HMD_Homology h1, HMD_Homology_Marker hm1, ' + \
'HMD_Homology h2, HMD_Homology_Marker hm2, MRK_Marker m2 ' + \
'where hm1._Marker_key = m._Marker_key ' + \
'and hm1._Homology_key = h1._Homology_key ' + \
'and h1._Class_key = h2._Class_key ' + \
'and h2._Homology_key = hm2._Homology_key ' + \
'and hm2._Marker_key = m2._Marker_key ' + \
'and m2._Species_key = 2) ' + \
'union ' + \
'select distinct m._Marker_key ' + \
'from #markers m ' + \
'where exists (select 1 from HMD_Homology h1, HMD_Homology_Marker hm1, ' + \
'HMD_Homology h2, HMD_Homology_Marker hm2, MRK_Marker m2 ' + \
'where hm1._Marker_key = m._Marker_key ' + \
'and hm1._Homology_key = h1._Homology_key ' + \
'and h1._Class_key = h2._Class_key ' + \
'and h2._Homology_key = hm2._Homology_key ' + \
'and hm2._Marker_key = m2._Marker_key ' + \
'and m2._Species_key = 40) ')

cmds.append('create nonclustered index index_marker_key on #markers(_Marker_key)')

cmds.append('select distinct m.*, r._Refs_key, r.jnum, r.jnumID, r.short_citation, b.dbs ' + \
'into #references ' + \
'from #markers m , MRK_Reference_View r, BIB_Refs b ' + \
'where m._Marker_key = r._Marker_key ' + \
'and r._Refs_key = b._Refs_key')

cmds.append('select distinct _Marker_key, symbol, name, mgiID, numRefs = count(_Refs_key) ' + \
'from #references ' + \
'where jnum not in (23000, 57747, 63103, 57676, 67225, 67226) ' + \
'and short_citation not like "%Genbank Submission%" ' + \
'group by _Marker_key ' + \
'order by symbol')

cmds.append('select distinct _Marker_key, symbol, name, mgiID, numRefs = count(_Refs_key) ' + \
'from #references group by _Marker_key ' + \
'order by symbol')

cmds.append('select distinct _Marker_key, symbol, name, mgiID, numRefs = count(_Refs_key) ' + \
'from #references ' + \
'where jnum in (23000, 57747, 63103, 57676, 67225, 67226) ' + \
'and short_citation not like "%Genbank Submission%" ' + \
'group by _Marker_key ' + \
'order by symbol')

cmds.append('select distinct _Marker_key, symbol, name, mgiID, jnumID, numericPart ' + \
'from #references ' + \
'where dbs like "%GO%" and dbs not like "%GO*%" ' + \
'order by numericPart')

results = db.sql(cmds, 'auto')

# Process homology info
hasHomology = {}
for r in results[1]:
	hasHomology[r['_Marker_key']] = 1

for r in results[-4]:
	writeRecord(fpA, r)

for r in results[-3]:
	writeRecord(fpB, r)

for r in results[-2]:
	writeRecord(fpC, r)

for r in results[-1]:
	writeRecordD(fpD, r)

reportlib.finish_nonps(fpA)	# non-postscript file
reportlib.finish_nonps(fpB)	# non-postscript file
reportlib.finish_nonps(fpC)	# non-postscript file
reportlib.finish_nonps(fpD)	# non-postscript file

