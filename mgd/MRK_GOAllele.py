#!/usr/local/bin/python

'''
#
# MRK_GOAllele.py 01/11/2002
#
# Report:
#       TR 3775
#
#	Title = Markers w/ GO Annotations where
#               the marker has 'GO' association w/ IMP
#		the "inferred from" field is null
#               the reference is a reference for one or more Alleles
#
#       Report in a tab delimited file with the following columns:
#
#    		symbol
#		GO ID
#		GO Term
#		J#
#		Allele ID, Allele ID, etc.
#
# Usage:
#       MRK_GOAllele.py
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
# lec	01/11/2002
#	- created
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

#
# Main
#

title = 'Markers w/ GO Annotations where the Evidence Code = IMP, Inferred From = NULL\n' + \
        'and the Annotation Reference is associated with one or more Alleles\n'
fp = reportlib.init(sys.argv[0], title = title, outputdir = os.environ['QCREPORTOUTPUTDIR'])

fp.write(string.ljust('symbol', 27) + \
	 string.ljust('goID', 32) + \
 	 string.ljust('term', 52) + \
 	 string.ljust('jnumID', 12) + \
 	 'alleles' + CRT)

fp.write('-' * 25 + '  ' + \
	 '-' * 30 + '  ' + \
	 '-' * 50 + '  ' + \
	 '-' * 10 + '  ' + \
	 '-' * 50 + CRT)

cmds = []

#
# select markers with GO annotations to IMP where inferredFrom is null
#
cmds.append('select m._Marker_key, m.symbol, goID = a.accID, term = substring(a.term,1,50), e._Refs_key, e.jnumID ' + \
'into #m1 ' + \
'from MRK_Marker m, VOC_Annot_View a, VOC_Evidence_View e ' + \
'where m._Organism_key = 1 ' + \
'and m._Marker_Type_key = 1 ' + \
'and m._Marker_Status_key in (1,3) ' + \
'and m._Marker_key = a._Object_key ' + \
'and a._AnnotType_key = 1000 ' + \
'and a._Annot_key = e._Annot_key ' + \
'and e._EvidenceTerm_key = 110 ' + \
'and e.inferredFrom is null')

cmds.append('create nonclustered index idx_refs_key on #m1(_Refs_key)')

#
# select alleles from set 1 which are associated with the annotation references
#
cmds.append('select m.*, alleleID = a.accID ' + \
'into #m2 ' + \
'from #m1 m, ALL_Reference r, ACC_Accession a ' + \
'where m._Refs_key = r._Refs_key ' + \
'and r._Allele_key = a._Object_key ' + \
'and a._MGIType_key = 11 ' + \
'and a.preferred = 1')

#
# select the allele ids so we can build a dictionary of marker/ref => allele associations
#
cmds.append('select distinct _Marker_key, _Refs_key, alleleID from #m2')

#
# select the markers which have associated alleles
#
cmds.append('select distinct _Marker_key, _Refs_key, symbol, goID, term, jnumID from #m2 order by symbol')

results = db.sql(cmds, 'auto')

# store dictionary of alleles by marker/reference
alleles = {}
for r in results[3]:
	key = `r['_Marker_key']` + ':' + `r['_Refs_key']`
	if not alleles.has_key(key):
		alleles[key] = []
	alleles[key].append(r['alleleID'])

rows = 0
for r in results[4]:
	key = `r['_Marker_key']` + ':' + `r['_Refs_key']`

	fp.write(string.ljust(r['symbol'], 27) + \
	 	 string.ljust(r['goID'], 32) + \
	 	 string.ljust(r['term'], 52) + \
	 	 string.ljust(r['jnumID'], 12) + \
	 	 string.joinfields(alleles[key], ',') + CRT)
	rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))
reportlib.trailer(fp)
reportlib.finish_nonps(fp)	# non-postscript file

