#!/usr/local/bin/python

'''
#
# SEQ_GenBank.py 10/17/2003
#
# Report:
#	TR 5226
#
#       Tab-delimited file
#       Nucleotide Sequence Accession numbers and the objects associated with them.
#
#	Seq ID
#	Pipe-delimited (|) tuple of:
#		object type (Marker, Segment)
#		object "name" (Marker Type or Segment Name)
#		object MGI ID
#		object symbol (for Segment, the symbol of the Marker with the E, P or H relationship)
#		if Segment, relationship (E, P, H, N if null)
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

markerType = 'Marker:'
segmentType = 'Segment:'

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCREPORTOUTPUTDIR'], printHeading = 0)

db.useOneConnection(1)

# select all RefSeq/GenBank Seq IDs/Mouse Markers

cmds = []

cmds.append('select a2._Object_key, a1.accID ' + \
	'into #seq1 ' + \
	'from ACC_Accession a2, ACC_Accession a1, MRK_Marker m ' + \
	'where a2._MGIType_key = 2 ' + \
	'and a2._LogicalDB_key in (9,27) ' + \
	'and a2.accID = a1.accID ' + \
	'and a1._MGIType_key = 19 ' + \
	'and a2._LogicalDB_key = a1._LogicalDB_key ' + \
	'and a2._Object_key = m._Marker_key ' + \
	'and m._Organism_key = 1')

cmds.append('create nonclustered index idx1 on #seq1(_Object_key)')
cmds.append('create nonclustered index idx2 on #seq1(accID)')

# select all unique Marker objects

cmds.append('select distinct _Object_key into #uniqo1 from #seq1')
cmds.append('create nonclustered index idx1 on #uniqo1(_Object_key)')

db.sql(cmds, None)
print 'query 1 (marker sequences) end...%s' % (mgi_utils.date())

# select all RefSeq/GenBank Seq IDs/Segments

cmds = []

cmds.append('select a2._Object_key, a1.accID ' + \
	'into #seq2 ' + \
	'from ACC_Accession a2, ACC_Accession a1 ' + \
	'where a2._MGIType_key = 3 ' + \
	'and a2._LogicalDB_key in (9,27) ' + \
	'and a2.accID = a1.accID ' + \
	'and a1._MGIType_key = 19 ' + \
	'and a2._LogicalDB_key = a1._LogicalDB_key')

cmds.append('create nonclustered index idx1 on #seq2(_Object_key)')
cmds.append('create nonclustered index idx2 on #seq2(accID)')

# select all unique Segment objects

cmds.append('select distinct _Object_key into #uniqo2 from #seq2')
cmds.append('create nonclustered index idx1 on #uniqo2(_Object_key)')

db.sql(cmds, None)
print 'query 2 (segment sequences) end...%s' % (mgi_utils.date())

# select MGI IDs for all Markers

cmds = []
cmds.append('select s._Object_key, a.accID ' +
'into #mgiIDs1 ' + 
'from #uniqo1 s, ACC_Accession a ' + \
'where s._Object_key = a._Object_key ' + \
'and a._MGIType_key = 2 ' + \
'and a._LogicalDB_key = 1 ' + \
'and a.prefixPart = "MGI:" ' + \
'and a.preferred = 1 ')
db.sql(cmds, None)
print 'query 3 (mgi ids) end...%s' % (mgi_utils.date())

# select MGI IDs for all Segments

cmds = []
cmds.append('select s._Object_key, a.accID ' +
'into #mgiIDs2 ' +
'from #uniqo2 s, ACC_Accession a ' + \
'where s._Object_key = a._Object_key ' + \
'and a._MGIType_key = 3 ' + \
'and a._LogicalDB_key = 1 ' + \
'and a.prefixPart = "MGI:" ' + \
'and a.preferred = 1 ')
db.sql(cmds, None)
print 'query 4 (mgi ids) end...%s' % (mgi_utils.date())

# select "names" (marker type for markers)

db.sql('select s._Object_key, t.name into #names1 ' + 
'from #uniqo1 s, MRK_Marker m, MRK_Types t ' + \
'where s._Object_key = m._Marker_key ' + \
'and m._Marker_Type_key = t._Marker_Type_key', None)
print 'query 5 (names) end...%s' % (mgi_utils.date())

# select "names" (name for molecular segments)

db.sql('select s._Object_key, p.name into #names2 ' + \
'from #uniqo2 s, PRB_Probe p ' + \
'where s._Object_key = p._Probe_key', None)
print 'query 6 (names) end...%s' % (mgi_utils.date())

# select "symbols" (symbols for markers)

db.sql('select s._Object_key, m.symbol into #symbols1 ' + \
'from #uniqo1 s, MRK_Marker m ' + \
'where s._Object_key = m._Marker_key', None)
print 'query 7 (symbols) end...%s' % (mgi_utils.date())

# select "symbols" (associated marker symbols & relationship for segments)

db.sql('select s._Object_key, symbol = m.symbol + ":" + pm.relationship into #symbols2 ' + \
'from #uniqo2 s, PRB_Marker pm, MRK_Marker m ' + \
'where s._Object_key = pm._Probe_key ' + \
'and pm._Marker_key = m._Marker_key', None)
print 'query 8 (symbols) end...%s' % (mgi_utils.date())

# set of sequence accession ids keyed by accession id
# for each sequence accession id, store the list of objects
# associated with it (by type and key).  then we can lookup
# the mgi accession id, name and symbol for each object
# using the other dictionaries.

results = db.sql('select distinct _Object_key, accID from #seq1', 'auto')
print 'query 9 (seq ids) end...%s' % (mgi_utils.date())
accIDs = {}
for r in results:
    key = regsub.gsub('\n', '', r['accID'])
    value = markerType + str(r['_Object_key'])
    if not accIDs.has_key(key):
	accIDs[key] = []
    accIDs[key].append(value)

results = db.sql('select distinct _Object_key, accID from #seq2', 'auto')
print 'query 10 (seq ids) end...%s' % (mgi_utils.date())
for r in results:
    key = regsub.gsub('\n', '', r['accID'])
    value = segmentType + str(r['_Object_key'])
    if not accIDs.has_key(key):
	accIDs[key] = []
    accIDs[key].append(value)

# set of mgi ids keyed by mgi type/object key

results = db.sql('select _Object_key, accID from #mgiIDs1', 'auto')
print 'query 11 (mgi ids) end...%s' % (mgi_utils.date())
mgiIDs = {}
for r in results:
    key = markerType + str(r['_Object_key'])
    value = regsub.gsub('\n', '', r['accID'])
    mgiIDs[key] = value

results = db.sql('select _Object_key, accID from #mgiIDs2', 'auto')
print 'query 12 (mgi ids) end...%s' % (mgi_utils.date())
for r in results:
    key = segmentType + str(r['_Object_key'])
    value = regsub.gsub('\n', '', r['accID'])
    mgiIDs[key] = value

# set of names keyed by mgi type/object key

results = db.sql('select _Object_key, name from #names1', 'auto')
print 'query 13 (names) end...%s' % (mgi_utils.date())
names = {}
for r in results:
    key = markerType + str(r['_Object_key'])
    value = r['name']
    names[key] = value

results = db.sql('select _Object_key, name from #names2', 'auto')
print 'query 14 (names) end...%s' % (mgi_utils.date())
for r in results:
    key = segmentType + str(r['_Object_key'])
    value = r['name']
    names[key] = value

# set of symbols keyed by mgi type/object key

results = db.sql('select _Object_key, symbol from #symbols1', 'auto')
print 'query 15 (symbols) end...%s' % (mgi_utils.date())
symbols = {}
for r in results:
    key = markerType + str(r['_Object_key'])
    value = r['symbol']
    if not symbols.has_key(key):
	symbols[key] = []
    symbols[key].append(value)

results = db.sql('select _Object_key, symbol from #symbols2', 'auto')
print 'query 16 (symbols) end...%s' % (mgi_utils.date())
for r in results:
    key = segmentType + str(r['_Object_key'])
    value = r['symbol']
    if not symbols.has_key(key):
	symbols[key] = []
    symbols[key].append(value)

# for each sorted Sequence Accession ID

accKeys = accIDs.keys()
accKeys.sort()

for accID in accKeys:

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
db.useOneConnection(0)
