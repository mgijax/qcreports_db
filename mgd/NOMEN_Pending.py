#!/usr/local/bin/python

'''
#
# NOMEN_Reserved.py
#
# Report:
#       TR 3084
#	Nomen -Pending Symbols for Hes Wain (HUGO Human Nomenclature Committee)
#
# Usage:
#       NOMEN_Pending.py
#
# Notes:
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
#
# lec	11/06/2001
#	- created
#
'''
 
import sys 
import os
import string
import regsub
import db
import reportlib
import mgi_utils

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = 0)

cmds = []

#
# Get -pending symbols
#

cmds.append('select m._Marker_key, m.symbol, m.name, mgiID = a.accID, ' + \
'n._Nomen_key, createdBy = u.login, modDate = convert(char(10), n.modification_date, 101) ' + \
'into #pending ' + \
'from MRK_Marker m, ACC_Accession a, NOM_Marker n, MGI_User u ' + \
'where m._Marker_Status_key = 3 ' + \
'and m._Marker_key = a._Object_key ' + \
'and a._MGIType_key = 2 ' + \
'and a.prefixPart = "MGI:" ' + \
'and a._LogicalDB_key = 1 ' + \
'and a.preferred = 1' + \
'and m.symbol = n.symbol ' + \
'and n._CreatedBy_key = u._User_key ' + \
'union ' + \
'select m._Marker_key, m.symbol, m.name, mgiID = a.accID, NULL, NULL, NULL ' + \
'from MRK_Marker m, ACC_Accession a ' + \
'where m._Marker_Status_key = 3 ' + \
'and m._Marker_key = a._Object_key ' + \
'and a._MGIType_key = 2 ' + \
'and a.prefixPart = "MGI:" ' + \
'and a._LogicalDB_key = 1 ' + \
'and a.preferred = 1' + \
'and not exists (select 1 from NOM_Marker n, MGI_User u ' + \
'where m.symbol = n.symbol ' + \
'and n._CreatedBy_key = u._User_key)')


#
# Get PubMed IDs of primary reference
#

cmds.append('select p._Marker_key, a.accID ' + \
'from #pending p, ACC_Accession a, MGI_Reference_Nomen_View r ' + \
'where p._Nomen_key = r._Object_key ' + \
'and r.assocType = "Primary" ' + \
'and r._Refs_key = a._Object_key ' + \
'and a._MGIType_key = 1 ' + \
'and a._LogicalDB_Key = 29 ')

#
# Get Seq ID
#

cmds.append('select p._Marker_key, a.accID from #pending p, ACC_Accession a ' + \
'where p._Marker_key = a._Object_key ' + \
'and a._MGIType_key = 2 ' + \
'and a._LogicalDB_Key = 9 ')

#
# Get Synonyms
#

cmds.append('select p._Marker_key, s.synonym ' + \
'from #pending p, MGI_Synonym s, MGI_SynonymType st ' + \
'where p._Marker_key = s._Object_key ' + \
'and s._MGIType_key = 2 ' + \
'and s._SynonymType_key = st._SynonymType_key ' + \
'and st.synonymType = "exact"')

#
# Get Human Homologies
#

cmds.append('select p._Marker_key, hmarkerkey = h.markerKey2, hsymbol = h.marker2 ' + \
'into #homology ' + \
'from #pending p, HMD_Homology_Pairs_View h ' + \
'where p._Marker_key = h.markerkey1 ' + \
'and h.organismkey2 = 2 ')

cmds.append('select _Marker_key, hsymbol from #homology')

#
# Get Human Seq IDs
#

cmds.append('select h._Marker_key, a.accID from #homology h, ACC_Accession a ' + \
'where h.hmarkerkey = a._Object_key ' + \
'and a._MGIType_key = 2 ' + \
'and a._LogicalDB_Key = 9 ')

cmds.append('select * from #pending order by symbol')

results = db.sql(cmds, 'auto')

prevNomen = ''
accids = {}
pubmedids = {}
syns = {}
homologs = {}
humanaccids = {}

for r in results[1]:
	pubmedids[r['_Marker_key']] = r['accID']

for r in results[2]:
	accids[r['_Marker_key']] = r['accID']

for r in results[3]:
	if syns.has_key(r['_Marker_key']):
		syns[r['_Marker_key']].append(r['synonym'])
	else:
		syns[r['_Marker_key']] = []
		syns[r['_Marker_key']].append(r['synonym'])
	
for r in results[5]:
	homologs[r['_Marker_key']] = r['hsymbol']

for r in results[6]:
	if humanaccids.has_key(r['_Marker_key']):
		humanaccids[r['_Marker_key']].append(r['accID'])
	else:
		humanaccids[r['_Marker_key']] = []
		humanaccids[r['_Marker_key']].append(r['accID'])

for r in results[-1]:

	fp.write(r['mgiID'] + TAB)
	fp.write(r['symbol'] + TAB)
	fp.write(r['name'] + TAB)
	fp.write(mgi_utils.prvalue(r['createdBy']) + TAB)
	fp.write(mgi_utils.prvalue(r['modDate']) + TAB)

	if accids.has_key(r['_Marker_key']):
		fp.write(accids[r['_Marker_key']])
	fp.write(TAB)

	if pubmedids.has_key(r['_Marker_key']):
		fp.write(pubmedids[r['_Marker_key']])
	fp.write(TAB)

	if syns.has_key(r['_Marker_key']):
		fp.write(string.joinfields(syns[r['_Marker_key']], "|"))
	fp.write(TAB)

	if homologs.has_key(r['_Marker_key']):
		fp.write(homologs[r['_Marker_key']])
	fp.write(TAB)

	if humanaccids.has_key(r['_Marker_key']):
		fp.write(string.joinfields(humanaccids[r['_Marker_key']], "|"))
	fp.write(TAB)

	fp.write(CRT)

reportlib.finish_nonps(fp)

