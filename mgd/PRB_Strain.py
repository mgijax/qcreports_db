#!/usr/local/bin/python

'''
#
# PRB_Strain.py 09/27/2001
#
# Report:
#       Tab-delimited file
#       All Strains
#
# Usage:
#       PRB_Strain.py
#
# Used by:
#       Internal Report
#
# Notes:
#
# History:
#
# lec	09/27/2001
#	- TR 2541
#
'''
 
import sys
import os
import string
import db
import mgi_utils
import reportlib

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCREPORTOUTPUTDIR'], printHeading = 0)

cmds = []

# Retrieve MGI Accession number

cmds.append('select distinct a._Object_key, a.accID from PRB_Strain_Acc_View a ' + \
	'where a._LogicalDB_key = 1 and a.prefixPart = "MGI:" and a.preferred = 1')

# External Accession IDs

cmds.append('select distinct a._Object_key, a.accID from PRB_Strain_Acc_View a where a._LogicalDB_key != 1')

# Retrieve markers

cmds.append('select _Strain_key, symbol from PRB_Strain_Marker_View')

# Retrieve synonyms

cmds.append('select _Strain_key, synonym from PRB_Strain_Synonym')

# Retrieve all Strains

cmds.append('select _Strain_key, strain, private from PRB_Strain order by strain')

results = db.sql(cmds, 'auto')

mgiIDs = {}
externalIDs = {}
markers = {}
syns = {}

for r in results[0]:
	mgiIDs[r['_Object_key']] = r['accID']
	
for r in results[1]:
	if externalIDs.has_key(r['_Object_key']):
		externalIDs[r['_Object_key']].append(r['accID'])
	else:
		externalIDs[r['_Object_key']] = []
		externalIDs[r['_Object_key']].append(r['accID'])
	
for r in results[2]:
	if markers.has_key(r['_Strain_key']):
		markers[r['_Strain_key']].append(r['symbol'])
	else:
		markers[r['_Strain_key']] = []
		markers[r['_Strain_key']].append(r['symbol'])

for r in results[3]:
	if syns.has_key(r['_Strain_key']):
		syns[r['_Strain_key']].append(r['synonym'])
	else:
		syns[r['_Strain_key']] = []
		syns[r['_Strain_key']].append(r['synonym'])

for r in results[4]:
	if mgiIDs.has_key(r['_Strain_key']):
		fp.write(mgiIDs[r['_Strain_key']] + reportlib.TAB)
	else:
		fp.write(reportlib.TAB)

	fp.write(r['strain'] + reportlib.TAB)

	if markers.has_key(r['_Strain_key']):
		fp.write(string.joinfields(markers[r['_Strain_key']], '|') + reportlib.TAB)
	else:
		fp.write(reportlib.TAB)

	if externalIDs.has_key(r['_Strain_key']):
		fp.write(string.joinfields(externalIDs[r['_Strain_key']], '|') + reportlib.TAB)
	else:
		fp.write(reportlib.TAB)

	if syns.has_key(r['_Strain_key']):
		fp.write(string.joinfields(syns[r['_Strain_key']], '|') + reportlib.TAB)
	else:
		fp.write(reportlib.TAB)

	fp.write(`r['private']` + reportlib.CRT)

reportlib.finish_nonps(fp)

