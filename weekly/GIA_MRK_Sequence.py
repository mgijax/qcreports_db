#!/usr/local/bin/python

'''
#
# MRK_Sequence.py 03/02/99
#
# Report:
#       Tab-delimited file
#       Mouse Markers and their Nucleotide Sequence Accession numbers.
#	and their UniGene Accession numbers (TR 1631).
#
# Usage:
#       MRK_Sequence.py
#
# Used by:
#       Those establishing relationships between MGI Markers
#	and Nucleotide Sequences.
#
# History:
#
# lec	02/09/2011
#       - this is similar to the report on public, but specific for Sophia
#         and the ${MGD_DBUTILS}/bin/generateGIAssoc.csh product
#
# lec	01/27/2005
#	- TR 6529
#
# lec	12/18/2003
#	- TR 5440; added Marker Type
#
# lec	05/30/1999
#	- TR 1631; add UniGene Accession numbers
#
# lec	03/02/1999
#	- TR 130; now use direct Marker-Seq ID relationships
#
# lec	01/18/1999
#	- missing Segment records where relationship is null
#
# lec	01/13/98
#	- added comments section
#
# NOTE: This report is a variation of the daily report with the same name.
#       It does not get copied to the FTP site and is only used by the
#       mgddbutilities product to generate input files for the DFCI, DOTS
#       and NIA association loads.
#
'''
 
import sys
import os
import string
import mgi_utils
import reportlib

try:
    if os.environ['DB_TYPE'] == 'postgres':
        import pg_db
        db = pg_db
        db.setTrace()
        db.setAutoTranslateBE()
    else:
        import db
except:
    import db


#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)

# all official/interim mouse markers that have at least one Sequence ID

db.sql('''
	select m._Marker_key, m.symbol, m.name, m.chromosome, 
		o.offset, 
		upper(substring(s.status, 1, 1)) as markerStatus, 
		t.name as markerType
	into #markers 
	from MRK_Marker m, MRK_Offset o, MRK_Status s, MRK_Types t 
	where m._Organism_key = 1 
	and m._Marker_Status_key in (1,3) 
	and m._Marker_key = o._Marker_key 
	and o.source = 0 
	and m._Marker_Status_key = s._Marker_Status_key 
	and m._Marker_Type_key = t._Marker_Type_key 
	and exists (select 1 from ACC_Accession a where m._Marker_key = a._Object_key 
		and a._MGIType_key = 2 
		and a._LogicalDB_key in (9, 27) 
		and a.prefixPart not in ('XP_', 'NP_'))
	''', None)
db.sql('create index idx1 on #markers(_Marker_key)', None)
db.sql('create index idx2 on #markers(symbol)', None)

# MGI ids

results = db.sql('''
	select distinct m._Marker_key, a.accID 
      	from #markers m, ACC_Accession a 
      	where m._Marker_key = a._Object_key 
      	and a._MGIType_key = 2 
      	and a._LogicalDB_key = 1 
      	and a.prefixPart = 'MGI:' 
      	and a.preferred = 1
	''', 'auto')
mgiID = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    mgiID[key] = value

# GenBank ids

results = db.sql('''
	select distinct m._Marker_key, a.accID 
      	from #markers m, ACC_Accession a 
      	where m._Marker_key = a._Object_key 
      	and a._MGIType_key = 2 
      	and a._LogicalDB_key = 9
	''', 'auto')
gbID = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not gbID.has_key(key):
	gbID[key] = []
    gbID[key].append(value)

# UniGene ids

results = db.sql('''
	select distinct m._Marker_key, a.accID 
      	from #markers m, ACC_Accession a 
      	where m._Marker_key = a._Object_key 
      	and a._MGIType_key = 2 
      	and a._LogicalDB_key = 23
	''', 'auto')
ugID = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not ugID.has_key(key):
	ugID[key] = []
    ugID[key].append(value)

# RefSeq ids

results = db.sql('''
	select distinct m._Marker_key, a.accID 
      	from #markers m, ACC_Accession a 
      	where m._Marker_key = a._Object_key 
      	and a._MGIType_key = 2 
      	and a._LogicalDB_key = 27 
      	and a.prefixPart not in ('XP_', 'NP_')
	''', 'auto')
rsID = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not rsID.has_key(key):
	rsID[key] = []
    rsID[key].append(value)

# process

results = db.sql('select * from #markers order by symbol', 'auto')

for r in results:
	key = r['_Marker_key']

	if r['offset'] == -1.0:
		offset = 'syntenic'
	elif r['offset'] == -999.0:
		offset = 'N/A'
	else:
		offset = str(r['offset'])

	fp.write(mgiID[key] + reportlib.TAB + \
	       	 r['symbol'] + reportlib.TAB + \
	       	 r['markerStatus'] + reportlib.TAB + \
	         r['markerType'] + reportlib.TAB + \
	         r['name'] + reportlib.TAB + \
	         offset + reportlib.TAB + \
	         r['chromosome'] + reportlib.TAB)

	if gbID.has_key(key):
		fp.write(string.join(gbID[key], ' '))
	fp.write(reportlib.TAB)

	if ugID.has_key(key):
		fp.write(string.join(ugID[key], ' '))
	fp.write(reportlib.TAB)

	if rsID.has_key(key):
		fp.write(string.join(rsID[key], ' '))
	fp.write(reportlib.CRT)

reportlib.finish_nonps(fp)
