#!/usr/local/bin/python

'''
#
# SEQ_GenBank.py 10/17/2003
#
# Report:
#	TR 5226
#
#       Tab-delimited file
#       Nucleotide Sequence Accession numbers
#	and the objects associated with them.
#
#	Seq ID
#	Pipe-delimited (|) tuple of:
#		object type (Marker, Molecular Segment)
#		object "name" (Marker Type or MS Name)
#		object MGI ID
#		object symbol (for MS, the symbol of the Marker with the E, P or H relationship)
#		if Molecular Segment, relationship (E, P, H, N if null)
#
# Usage:
#       SEQ_GenBank.py
#
# Used by:
#       Bob Sinclair (bobs)
#
# Notes:
#
# History:
#
# lec	10/17/2003
#	- new
#
'''
 
import sys
import os
import string
import regsub
import db
import mgi_utils
import reportlib

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCREPORTOUTPUTDIR'], printHeading = 0)

cmds = []

# select all Seq IDs and the Objects associated with them
# for Markers, only select Mouse

cmds.append('select distinct a.accID, a._Object_key, a._MGIType_key, mgiType = m.name ' + \
'into #seqIDs ' + \
'from PRB_Acc_View a, ACC_MGIType m ' + \
'where a._LogicalDB_key in (9,27) ' + \
'and a._MGIType_key = m._MGIType_key ' + \
'union ' + \
'select distinct a.accID, a._Object_key, a._MGIType_key, mgiType = m.name ' + \
'from MRK_Acc_View a, ACC_MGIType m, MRK_Marker k ' + \
'where a._LogicalDB_key in (9,27) ' + \
'and a._MGIType_key = m._MGIType_key ' + \
'and a._Object_key = k._Marker_key ' + \
'and k._Organism_key = 1')

cmds.append('create nonclustered index idx_accid on #seqIDs(accID)')
cmds.append('create nonclustered index idx_object on #seqIDs(_Object_key)')
cmds.append('create nonclustered index idx_type on #seqIDs(_MGIType_key)')

# select MGI IDs for all Objects

cmds.append('select distinct s._Object_key, s.mgiType, a.accID ' +
'into #mgiIDs ' + 
'from #seqIDs s, MRK_Acc_View a ' + \
'where s._MGIType_key = 2 ' + \
'and s._Object_key = a._Object_key ' + \
'and a._LogicalDB_key = 1 ' + \
'and a.prefixPart = "MGI:" ' + \
'and a.preferred = 1 ' + \
'union ' + \
'select distinct s._Object_key, s.mgiType, a.accID ' +
'from #seqIDs s, PRB_Acc_View a ' + \
'where s._MGIType_key = 3 ' + \
'and s._Object_key = a._Object_key ' + \
'and a._LogicalDB_key = 1 ' + \
'and a.prefixPart = "MGI:" ' + \
'and a.preferred = 1 ')

# select "names" (marker type for markers, name for molecular segments)

cmds.append('select distinct s._Object_key, s.mgiType, t.name ' +
'into #names ' + 
'from #seqIDs s, MRK_Marker m, MRK_Types t ' + \
'where s._MGIType_key = 2 ' + \
'and s._Object_key = m._Marker_key ' + \
'and m._Marker_Type_key = t._Marker_Type_key ' + \
'union ' + \
'select distinct s._Object_key, s.mgiType, p.name ' +
'from #seqIDs s, PRB_Probe p ' + \
'where s._MGIType_key = 3 ' + \
'and s._Object_key = p._Probe_key ')

# select symbols (symbols for markers and associated marker symbols for molecular segments)

cmds.append('select distinct s._Object_key, s.mgiType, m.symbol ' + \
'into #symbols ' + \
'from #seqIDs s, MRK_Marker m ' + \
'where s._MGIType_key = 2 ' + \
'and s._Object_key = m._Marker_key ' + \
'union ' + \
'select distinct s._Object_key, s.mgiType, symbol = pm.symbol + ":" + pm.relationship ' + \
'from #seqIDs s, PRB_Marker_View pm ' + \
'where s._MGIType_key = 3 ' + \
'and s._Object_key = pm._Probe_key')

# select each set of data

cmds.append('select * from #seqIDs')
cmds.append('select * from #mgiIDs')
cmds.append('select * from #names')
cmds.append('select * from #symbols')
cmds.append('select distinct accID from #seqIDs order by accID')

results = db.sql(cmds, 'auto')

# set of sequence accession ids keyed by accession id
# for each sequence accession id, store the list of objects
# associated with it (by type and key).  then we can lookup
# the mgi accession id, name and symbol for each object
# using the other dictionaries.

accIDs = {}
for r in results[-5]:
    key = regsub.gsub('\n', '', r['accID'])
    value = r['mgiType'] + ':' + str(r['_Object_key'])
    if not accIDs.has_key(key):
	accIDs[key] = []
    accIDs[key].append(value)

# set of mgi ids keyed by mgi type/object key

mgiIDs = {}
for r in results[-4]:
    key = r['mgiType'] + ':' + str(r['_Object_key'])
    value = regsub.gsub('\n', '', r['accID'])
    mgiIDs[key] = value

# set of names keyed by mgi type/object key

names = {}
for r in results[-3]:
    key = r['mgiType'] + ':' + str(r['_Object_key'])
    value = r['name']
    names[key] = value

# set of symbols keyed by mgi type/object key

symbols = {}
for r in results[-2]:
    key = r['mgiType'] + ':' + str(r['_Object_key'])
    value = r['symbol']
    if not symbols.has_key(key):
	symbols[key] = []
    symbols[key].append(value)

# for each Sequence Accession ID

for r in results[-1]:

    accID = regsub.gsub('\n', '', r['accID'])
    fp.write(accID)

    # for each Object associated with the Sequence Accession ID

    for mgiObject in accIDs[accID]:

	# extract name (and object key) for the Object
	[mgiName, objectKey] = string.split(mgiObject, ':')

	# if the Object has a symbol...

	if symbols.has_key(mgiObject):

	  # print out each Symbol in a separate tuple
	  for mgiSymbol in symbols[mgiObject]:

	      if string.find(mgiSymbol, ':') >= 0:
		  [symbol, rel] = string.split(mgiSymbol, ':')
		  if len(rel) == 0:
		      rel = 'N'
 	          fp.write(reportlib.TAB + mgiName + '|' + \
		           names[mgiObject] + '|' + \
		           mgiIDs[mgiObject] + '|' + \
		           symbol + '|' + \
			   rel)
	      else:
 	          fp.write(reportlib.TAB + mgiName + '|' + \
		           names[mgiObject] + '|' + \
		           mgiIDs[mgiObject] + '|' + \
		           mgiSymbol)

	# else, just print out the tuple with a blank Symbol

	else:
	    fp.write(reportlib.TAB + mgiName + '|' + \
		     names[mgiObject] + '|' + \
		     mgiIDs[mgiObject] + '|')

    fp.write(reportlib.CRT)

reportlib.finish_nonps(fp)

