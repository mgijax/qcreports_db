#!/usr/local/bin/python

'''
#
# MGI_AllStrains.py 02/04/2002
#
# Report:
#       Tab-delimited file
#       All Strains for JRS
#
# Usage:
#       MGI_AllStrains.py
#
# Used by:
#       JRS to load in new Strain data
#
# Output:
#
#	tab-delimited file
#
#	1. MGI ID
#	2. Strain Name
#	3. JRS ID
#	4. Markers (|-separated)
#	5. Strain Type (|-separated)
#	6. Synonyms (|-separated)
#	7. public/private
#
# Notes:
#
# History:
#
# lec	02/04/2002
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

# Retrieve MGI Accession numbers for all strains

cmds.append('select distinct a._Object_key, a.accID from PRB_Strain_Acc_View a ' + \
	'where a._LogicalDB_key = 1 and a.prefixPart = "MGI:" and a.preferred = 1')

# JRS Accession IDs

cmds.append('select distinct a._Object_key, a.accID from PRB_Strain_Acc_View a where a._LogicalDB_key = 22')

# Retrieve markers

cmds.append('select _Strain_key, symbol from PRB_Strain_Marker_View')

# Retrieve synonyms

cmds.append('select _Strain_key, synonym from PRB_Strain_Synonym')

# Retrieve strain types

cmds.append('select _Strain_key, strainType from MLP_StrainTypes_View')

# Retrieve all Strains

cmds.append('select _Strain_key, strain, private from PRB_Strain order by strain')

results = db.sql(cmds, 'auto')

mgiIDs = {}
jrsIDs = {}
markers = {}
syns = {}
stypes = {}

for r in results[0]:
	mgiIDs[r['_Object_key']] = r['accID']

for r in results[1]:
	if jrsIDs.has_key(r['_Object_key']):
		jrsIDs[r['_Object_key']].append(r['accID'])
	else:
		jrsIDs[r['_Object_key']] = []
		jrsIDs[r['_Object_key']].append(r['accID'])
	
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
	if stypes.has_key(r['_Strain_key']):
		stypes[r['_Strain_key']].append(r['strainType'])
	else:
		stypes[r['_Strain_key']] = []
		stypes[r['_Strain_key']].append(r['strainType'])

for r in results[5]:
	if mgiIDs.has_key(r['_Strain_key']):
		fp.write(mgiIDs[r['_Strain_key']] + reportlib.TAB)
	else:
		fp.write(reportlib.TAB)

	fp.write(r['strain'] + reportlib.TAB)

	if jrsIDs.has_key(r['_Strain_key']):
		fp.write(string.joinfields(jrsIDs[r['_Strain_key']], '|') + reportlib.TAB)
	else:
		fp.write(reportlib.TAB)

	if markers.has_key(r['_Strain_key']):
		fp.write(string.joinfields(markers[r['_Strain_key']], '|') + reportlib.TAB)
	else:
		fp.write(reportlib.TAB)

	if syns.has_key(r['_Strain_key']):
		fp.write(string.joinfields(syns[r['_Strain_key']], '|') + reportlib.TAB)
	else:
		fp.write(reportlib.TAB)

	if stypes.has_key(r['_Strain_key']):
		fp.write(string.joinfields(stypes[r['_Strain_key']], '|') + reportlib.TAB)
	else:
		fp.write(reportlib.TAB)

	if r['private'] == 1:
		status = 'private'
	else:
		status = 'public'

	fp.write(status + reportlib.CRT)

reportlib.finish_nonps(fp)

