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

markerType = 'Marker'
molsegType = 'Molecular Segment'

#
# Main
#

db.useOneConnection(1)
fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCREPORTOUTPUTDIR'], printHeading = 0)

print 'query 1 begin...%s' % (mgi_utils.date())
cmds = []
cmds.append('select a.accID, a._Object_key ' + \
	'into #mseqIDs ' + \
	'from ACC_Accession a, MRK_Marker m ' + \
	'where a._MGIType_key = 2 ' + \
	'and a._LogicalDB_key in (9,27) ' + \
	'and a._Object_key = m._Marker_key ' + \
	'and m._Organism_key = 1')
cmds.append('create index idx1 on #mseqIDs(accID)')
cmds.append('create index idx2 on #mseqIDs(_Object_key)')
db.sql(cmds, None)
print 'query 1 end...%s' % (mgi_utils.date())

print 'query 2 begin...%s' % (mgi_utils.date())
cmds = []
cmds.append('select accID, _Object_key ' + \
	'into #pseqIDs ' + \
	'from ACC_Accession ' + \
	'where _MGIType_key = 3 ' + \
	'and _LogicalDB_key in (9,27) ')
cmds.append('create index idx1 on #pseqIDs(accID)')
cmds.append('create index idx2 on #pseqIDs(_Object_key)')
db.sql(cmds, None)
print 'query 2 end...%s' % (mgi_utils.date())

#
# select MGI IDs for all Objects
# set of mgi ids keyed by mgi type/object key
#

print 'query 3 begin...%s' % (mgi_utils.date())
mgiIDs = {}
results = db.sql('select distinct s._Object_key, a.accID ' +
	'from #mseqIDs s, ACC_Accession a ' + \
	'where s._Object_key = a._Object_key ' + \
	'and a._MGIType_key = 2 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1 ', 'auto')
for r in results:
    key = markerType + ':' + str(r['_Object_key'])
    value = regsub.gsub('\n', '', r['accID'])
    mgiIDs[key] = value
print 'query 3 end...%s' % (mgi_utils.date())

print 'query 4 begin...%s' % (mgi_utils.date())
results = db.sql('select distinct s._Object_key, a.accID ' +
	'from #pseqIDs s, ACC_Accession a ' + \
	'where s._Object_key = a._Object_key ' + \
	'and a._MGIType_key = 3 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1 ', 'auto')
for r in results:
    key = molsegType + ':' + str(r['_Object_key'])
    value = regsub.gsub('\n', '', r['accID'])
    mgiIDs[key] = value
print 'query 4 end...%s' % (mgi_utils.date())

#
# select "names" (marker type for markers, name for molecular segments)
# set of names keyed by mgi type/object key
#

print 'query 5 begin...%s' % (mgi_utils.date())
names = {}
results = db.sql('select distinct s._Object_key, t.name ' +
	'from #mseqIDs s, MRK_Marker m, MRK_Types t ' + \
	'where s._Object_key = m._Marker_key ' + \
	'and m._Marker_Type_key = t._Marker_Type_key', 'auto')
for r in results:
    key = markerType + ':' + str(r['_Object_key'])
    value = r['name']
    names[key] = value
print 'query 5 end...%s' % (mgi_utils.date())

print 'query 6 begin...%s' % (mgi_utils.date())
results = db.sql('select distinct s._Object_key, p.name ' +
	'from #pseqIDs s, PRB_Probe p ' + \
	'where s._Object_key = p._Probe_key ', 'auto')
for r in results:
    key = molsegType + ':' + str(r['_Object_key'])
    value = r['name']
    names[key] = value
print 'query 6 end...%s' % (mgi_utils.date())

#
# select symbols (symbols for markers and associated marker symbols for molecular segments)
# set of symbols keyed by mgi type/object key
#

print 'query 7 begin...%s' % (mgi_utils.date())
symbols = {}
results = db.sql('select distinct s._Object_key, m.symbol ' + \
	'from #mseqIDs s, MRK_Marker m ' + \
	'where s._Object_key = m._Marker_key ', 'auto')
for r in results:
    key = markerType + ':' + str(r['_Object_key'])
    value = r['symbol']
    if not symbols.has_key(key):
	symbols[key] = []
    symbols[key].append(value)
print 'query 7 end...%s' % (mgi_utils.date())

print 'query 8 begin...%s' % (mgi_utils.date())
results = db.sql('select distinct s._Object_key, symbol = m.symbol + ":" + pm.relationship ' + \
	'from #pseqIDs s, PRB_Marker pm, MRK_Marker m ' + \
	'where s._Object_key = pm._Probe_key ' + \
	'and pm._Marker_key = m._Marker_key', 'auto')
for r in results:
    key = molsegType + ':' + str(r['_Object_key'])
    value = r['symbol']
    if not symbols.has_key(key):
	symbols[key] = []
    symbols[key].append(value)
print 'query 8 end...%s' % (mgi_utils.date())

####
#### process main data
####

# select each set of data

# set of sequence accession ids keyed by accession id
# for each sequence accession id, store the list of objects
# associated with it (by type and key).  then we can lookup
# the mgi accession id, name and symbol for each object
# using the other dictionaries.

print 'query 9 begin...%s' % (mgi_utils.date())
accIDs = {}
results = db.sql('select distinct accID, _Object_key from #mseqIDs', 'auto')
for r in results:
    key = regsub.gsub('\n', '', r['accID'])
    value = markerType + ':' + str(r['_Object_key'])
    if not accIDs.has_key(key):
	accIDs[key] = []
    accIDs[key].append(value)
results = db.sql('select distinct accID, _Object_key from #pseqIDs', 'auto')
for r in results:
    key = regsub.gsub('\n', '', r['accID'])
    value = molsegType + ':' + str(r['_Object_key'])
    if not accIDs.has_key(key):
	accIDs[key] = []
    accIDs[key].append(value)
print 'query 9 end...%s' % (mgi_utils.date())

print 'query 10 begin...%s' % (mgi_utils.date())
results = db.sql('select distinct accID from #mseqIDs ' + \
	'union ' + \
	'select distinct accID from #pseqIDs order by accID', 'auto')
print 'query 10 end...%s' % (mgi_utils.date())

# for each Sequence Accession ID

for r in results:

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
db.useOneConnection(0)

