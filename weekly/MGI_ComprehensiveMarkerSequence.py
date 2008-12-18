#!/usr/local/bin/python

'''
#
# MGI_ComprehensiveMarkerSequence.py
#
# Report:
#       TR9376
#       Comprehensive Marker/Sequence report
#	(reports_db/daily/MRK_Sequence.py was used as the template)
#
# This report will select ALL Marker (interim, official, withdrawn):
#
#  1: MGI ID
#  2: Symbol
#  3. Synonyms
#  4. History Symbol
#  5. Marker Status
#  6: Marker Type
#  7: Chromosome
#  8: Coordinates formatted as start..end
#
#  9. Representative Transcript (RNA)
# 10. Representative Genomic (DNA)
#
# note that all of the sequence ids includes both primary and secondary ids
#
# 11. Refseq IDs - all types, NM, NR, XM, etc (27)
# 12. Deleted refseq IDs (sequences) - again all types
#
# 13. Genbank IDs (9)
# 14. Deleted genbank IDs (sequences)
#
# 15. NCBI GeneIDs (59)
# 16. Ensembl ENSMUSG IDs (60)
# 17. VEGA OTTMUSG IDs (85)
#
# 18. DFCI/TIGR IDs (35)
# 19. DoTS IDs (36)
# 20. NIA IDs (53)
# 21. Unigene IDs (23)
#
# Usage:
#       MGI_ComprehensiveMarkerSequence.py
#
# Used by:
#
# History:
#
# lec	12/18/2008
#	- for 11-21, select all primary and secondary ids
#
# lec	12/10/2008
#	- added History Symbols column
#
# lec	12/09/2008
#	- added Synonyms column
#
# lec	11/20/2008
#	- TR9376
#
'''
 
import sys
import os
import string
import db
import mgi_utils
import reportlib

blankTag = '---'

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], printHeading = None)
fp.write('#\n')
fp.write('# This report selects all mouse Markers that:\n')
fp.write('#  are of any Status (interim, official, withdrawn)\n')
fp.write('#  contain a primary MGI ID\n')
fp.write('#\n')
fp.write('#  column 1: MGI ID\n')
fp.write('#  column 2: Symbol\n')
fp.write('#  column 3. Synonyms\n')
fp.write('#  column 4. History Symbol\n')
fp.write('#  column 5. Marker Status\n')
fp.write('#  column 6: Marker Type\n')
fp.write('#  column 7: Chromosome\n')
fp.write('#  column 8: Coordinates formatted as start..end\n')
fp.write('#  column 9. Representative Transcript (RNA)\n')
fp.write('#  column 10.Representative Genomic (DNA)\n')
fp.write('#  column 11. Refseq IDs - all types, NM, NR, XM, etc (27)\n')
fp.write('#  column 12. Deleted refseq IDs (sequences) - again all types\n')
fp.write('#  column 13. Genbank IDs (9)\n')
fp.write('#  column 14. Deleted genbank IDs (sequences)\n')
fp.write('#  column 15. NCBI GeneIDs (59)\n')
fp.write('#  column 16. Ensembl ENSMUSG IDs (60)\n')
fp.write('#  column 17. VEGA OTTMUSG IDs (85)\n')
fp.write('#  column 18. DFCI/TIGR IDs (35)\n')
fp.write('#  column 19. DoTS IDs (36)\n')
fp.write('#  column 20. NIA IDs (53)\n')
fp.write('#  column 21. Unigene IDs (23)\n')
fp.write('#\n\n')

# deleted sequences

db.sql('select s._Sequence_key into #deleted from SEQ_Sequence s where s._SequenceStatus_key = 316343', None)
db.sql('create index idx1 on #deleted(_Sequence_key)', None)

db.sql('''select a.accID, a._LogicalDB_key into #deletedIDs from #deleted d, ACC_Accession a
    where d._Sequence_key = a._Object_key
    and a._MGIType_key = 19''', None)
db.sql('create index idx1 on #deletedIDs(accID)', None)
db.sql('create index idx2 on #deletedIDs(_LogicalDB_key)', None)

# all mouse markers

db.sql('''select m._Marker_key, m.symbol, m.chromosome,
   markerStatus = upper(substring(s.status, 1, 1)), markerType = t.name,
   mgiID = a.accID, a.numericPart,
   startC = convert(int, c.startCoordinate),
   endC = convert(int, c.endCoordinate)
   into #markers
   from MRK_Marker m, MRK_Status s, MRK_Types t, ACC_Accession a, MRK_Location_Cache c
   where m._Organism_key = 1
   and m._Marker_Status_key = s._Marker_Status_key
   and m._Marker_Type_key = t._Marker_Type_key
   and m._Marker_key = a._Object_key
   and a._MGIType_key = 2
   and a._LogicalDB_key = 1
   and a.prefixPart = "MGI:"
   and a.preferred = 1
   and m._Marker_key = c._Marker_key
   ''', None)
db.sql('create index idx1 on #markers(_Marker_key)', None)
db.sql('create index idx2 on #markers(symbol)', None)
db.sql('create index idx3 on #markers(numericPart)', None)

# 3. Synonyms

mSynonym = {}
results = db.sql('''select distinct m._Marker_key, s.synonym
        from #markers m, MGI_Synonym s  
        where m._Marker_key = s._Object_key 
        and s._MGIType_key = 2''', 'auto')
for r in results:
    key = r['_Marker_key']
    value = r['synonym']
    if not mSynonym.has_key(key):
	mSynonym[key] = []
    mSynonym[key].append(value)

# 4. History Symbol

mHistory = {}
results = db.sql('''select distinct m._Marker_key, mm.symbol
        from #markers m, MRK_History s, MRK_Marker mm  
        where m._Marker_key = s._Marker_key 
	and s._History_key = mm._Marker_key''', 'auto')
for r in results:
    key = r['_Marker_key']
    value = r['symbol']
    if not mHistory.has_key(key):
	mHistory[key] = []
    mHistory[key].append(value)

# 9. Representative Transript (RNA)

repTran = {}
results = db.sql('''select m._Marker_key, a.accID
        from #markers m, SEQ_Marker_Cache smc, ACC_Accession a
        where m._Marker_key = smc._Marker_key
        and smc._Qualifier_key = 615420
        and smc._Sequence_key = a._Object_key
        and a._MGIType_key = 19
        and a.preferred = 1''', 'auto')
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    repTran[key] = value

# 10. Representative Genomic (DNA)

repGen = {}
results = db.sql('''select m._Marker_key, a.accID
        from #markers m, SEQ_Marker_Cache smc, ACC_Accession a
        where m._Marker_key = smc._Marker_key
        and smc._Qualifier_key = 615419
        and smc._Sequence_key = a._Object_key
        and a._MGIType_key = 19
        and a.preferred = 1''', 'auto')
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    repGen[key] = value

# the queries for 11-x will select all primary and secondary ids
# for all sequences associated with the marker

# 11. Refseq IDs - all types, NM, NR, XM, etc (27)

results = db.sql('''select distinct m._Marker_key, sa.accID
      from #markers m, SEQ_Marker_Cache a, ACC_Accession sa
      where m._Marker_key = a._Marker_key
      and a._LogicalDB_key = 27
      and a._Sequence_key = sa._Object_key
      and sa._MGIType_key = 19
      and a._LogicalDB_key = sa._LogicalDB_key
      and not exists (select 1 from #deletedIDs d where a.accID = d.accID and a._LogicalDB_key = d._LogicalDB_key)''', 'auto')
rsID = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not rsID.has_key(key):
	rsID[key] = []
    rsID[key].append(value)

# 12. Deleted refseq IDs (sequences) - again all types

results = db.sql('''select distinct m._Marker_key, sa.accID
      from #markers m, SEQ_Marker_Cache a, ACC_Accession sa
      where m._Marker_key = a._Marker_key
      and a._LogicalDB_key = 27
      and a._Sequence_key = sa._Object_key
      and sa._MGIType_key = 19
      and a._LogicalDB_key = sa._LogicalDB_key
      and exists (select 1 from #deletedIDs d where a.accID = d.accID and a._LogicalDB_key = d._LogicalDB_key)''', 'auto')
rsDelID = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not rsDelID.has_key(key):
	rsDelID[key] = []
    rsDelID[key].append(value)

# 13. Genbank IDs (9)

results = db.sql('''select distinct m._Marker_key, sa.accID
      from #markers m, SEQ_Marker_Cache a, ACC_Accession sa
      where m._Marker_key = a._Marker_key
      and a._LogicalDB_key = 9
      and a._Sequence_key = sa._Object_key
      and sa._MGIType_key = 19
      and a._LogicalDB_key = sa._LogicalDB_key
      and not exists (select 1 from #deletedIDs d where a.accID = d.accID and a._LogicalDB_key = d._LogicalDB_key)''', 'auto')
gbID = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not gbID.has_key(key):
	gbID[key] = []
    gbID[key].append(value)

# 14. Deleted genbank IDs (sequences)

results = db.sql('''select distinct m._Marker_key, sa.accID
      from #markers m, SEQ_Marker_Cache a, ACC_Accession sa
      where m._Marker_key = a._Marker_key
      and a._LogicalDB_key = 9
      and a._Sequence_key = sa._Object_key
      and sa._MGIType_key = 19
      and a._LogicalDB_key = sa._LogicalDB_key
      and exists (select 1 from #deletedIDs d where a.accID = d.accID and a._LogicalDB_key = d._LogicalDB_key)''', 'auto')
gbDelID = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not gbDelID.has_key(key):
	gbDelID[key] = []
    gbDelID[key].append(value)

# 15. NCBI GeneIDs (59)

results = db.sql('''select distinct m._Marker_key, sa.accID
      from #markers m, SEQ_Marker_Cache a, ACC_Accession sa
      where m._Marker_key = a._Marker_key
      and a._LogicalDB_key = 59
      and a._Sequence_key = sa._Object_key
      and sa._MGIType_key = 19
      and a._LogicalDB_key = sa._LogicalDB_key
      and not exists (select 1 from #deletedIDs d where a.accID = d.accID and a._LogicalDB_key = d._LogicalDB_key)''', 'auto')
ncbiID = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not ncbiID.has_key(key):
	ncbiID[key] = []
    ncbiID[key].append(value)

# UniGene ids

# 16. Ensembl ENSMUSG IDs (60)

results = db.sql('''select distinct m._Marker_key, sa.accID
      from #markers m, SEQ_Marker_Cache a, ACC_Accession sa
      where m._Marker_key = a._Marker_key
      and a._LogicalDB_key = 60
      and a._Sequence_key = sa._Object_key
      and sa._MGIType_key = 19
      and a._LogicalDB_key = sa._LogicalDB_key
      and not exists (select 1 from #deletedIDs d where a.accID = d.accID and a._LogicalDB_key = d._LogicalDB_key)''', 'auto')
ensemblID = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not ensemblID.has_key(key):
	ensemblID[key] = []
    ensemblID[key].append(value)

# 17. VEGA OTTMUSG IDs (85)

results = db.sql('''select distinct m._Marker_key, sa.accID
      from #markers m, SEQ_Marker_Cache a, ACC_Accession sa
      where m._Marker_key = a._Marker_key
      and a._LogicalDB_key = 85
      and a._Sequence_key = sa._Object_key
      and sa._MGIType_key = 19
      and a._LogicalDB_key = sa._LogicalDB_key
      and not exists (select 1 from #deletedIDs d where a.accID = d.accID and a._LogicalDB_key = d._LogicalDB_key)''', 'auto')
vegaID = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not vegaID.has_key(key):
	vegaID[key] = []
    vegaID[key].append(value)

# 18. DFCI/TIGR IDs (35)

results = db.sql('''select distinct m._Marker_key, sa.accID
      from #markers m, SEQ_Marker_Cache a, ACC_Accession sa
      where m._Marker_key = a._Marker_key
      and a._LogicalDB_key = 35
      and a._Sequence_key = sa._Object_key
      and sa._MGIType_key = 19
      and a._LogicalDB_key = sa._LogicalDB_key
      and not exists (select 1 from #deletedIDs d where a.accID = d.accID and a._LogicalDB_key = d._LogicalDB_key)''', 'auto')
dfciID = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not dfciID.has_key(key):
	dfciID[key] = []
    dfciID[key].append(value)

# 19. DoTS IDs (36)

results = db.sql('''select distinct m._Marker_key, sa.accID
      from #markers m, SEQ_Marker_Cache a, ACC_Accession sa
      where m._Marker_key = a._Marker_key
      and a._LogicalDB_key = 36
      and a._Sequence_key = sa._Object_key
      and sa._MGIType_key = 19
      and a._LogicalDB_key = sa._LogicalDB_key
      and not exists (select 1 from #deletedIDs d where a.accID = d.accID and a._LogicalDB_key = d._LogicalDB_key)''', 'auto')
dotsID = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not dotsID.has_key(key):
	dotsID[key] = []
    dotsID[key].append(value)

# 20. NIA IDs (53)

results = db.sql('''select distinct m._Marker_key, sa.accID
      from #markers m, SEQ_Marker_Cache a, ACC_Accession sa
      where m._Marker_key = a._Marker_key
      and a._LogicalDB_key = 53
      and a._Sequence_key = sa._Object_key
      and sa._MGIType_key = 19
      and a._LogicalDB_key = sa._LogicalDB_key
      and not exists (select 1 from #deletedIDs d where a.accID = d.accID and a._LogicalDB_key = d._LogicalDB_key)''', 'auto')
niaID = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not niaID.has_key(key):
	niaID[key] = []
    niaID[key].append(value)

# 21. Unigene IDs (23)

results = db.sql('''select distinct m._Marker_key, sa.accID
      from #markers m, SEQ_Marker_Cache a, ACC_Accession sa
      where m._Marker_key = a._Marker_key
      and a._LogicalDB_key = 23
      and a._Sequence_key = sa._Object_key
      and sa._MGIType_key = 19
      and a._LogicalDB_key = sa._LogicalDB_key
      and not exists (select 1 from #deletedIDs d where a.accID = d.accID and a._LogicalDB_key = d._LogicalDB_key)''', 'auto')
unigeneID = {}
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    if not unigeneID.has_key(key):
	unigeneID[key] = []
    unigeneID[key].append(value)

# process

results = db.sql('select * from #markers order by numericPart', 'auto')

for r in results:
	key = r['_Marker_key']

	#  1: MGI ID
	#  2: Symbol

	fp.write(r['mgiID'] + reportlib.TAB + \
	       	 r['symbol'] + reportlib.TAB)

	#  3: Synonym

	if mSynonym.has_key(key):
		fp.write(string.join(mSynonym[key], '|'))
	else:
		fp.write(blankTag)
	fp.write(reportlib.TAB)

	#  4: History Symbol

	if mHistory.has_key(key):
		fp.write(string.join(mHistory[key], '|'))
	else:
		fp.write(blankTag)
	fp.write(reportlib.TAB)

	#  5. Marker Status
	#  6: Marker Type
	#  7: Chromosome

	fp.write(r['markerStatus'] + reportlib.TAB + \
	         r['markerType'] + reportlib.TAB + \
	         r['chromosome'] + reportlib.TAB)

	#  8: Coordinates formatted as start..end

        if r['startC'] != None:
		fp.write(str(r['startC']) + '..' + str(r['endC']))
	else:
		fp.write(blankTag)
	fp.write(reportlib.TAB)

	#  9. Representative Transcript (RNA)

	if repTran.has_key(key):
		fp.write(repTran[key])
	else:
		fp.write(blankTag)
	fp.write(reportlib.TAB)

	#  10. Representative Genomic (DNA)

	if repGen.has_key(key):
		fp.write(repGen[key])
	else:
		fp.write(blankTag)
	fp.write(reportlib.TAB)

	# 11. Refseq IDs - all types, NM, NR, XM, etc

	if rsID.has_key(key):
		fp.write(string.join(rsID[key], ' '))
	else:
		fp.write(blankTag)
	fp.write(reportlib.TAB)

	# 12. Deleted refseq IDs (sequences) - again all types

	if rsDelID.has_key(key):
		fp.write(string.join(rsDelID[key], ' '))
	else:
		fp.write(blankTag)
	fp.write(reportlib.TAB)

	# 13. Genbank IDs

	if gbID.has_key(key):
		fp.write(string.join(gbID[key], ' '))
	else:
		fp.write(blankTag)
	fp.write(reportlib.TAB)

	# 14. Deleted genbank IDs (sequences)

	if gbDelID.has_key(key):
		fp.write(string.join(gbDelID[key], ' '))
	else:
		fp.write(blankTag)
	fp.write(reportlib.TAB)

	# 15. NCBI GeneIDs (59)

	if ncbiID.has_key(key):
		fp.write(string.join(ncbiID[key], ' '))
	else:
		fp.write(blankTag)
	fp.write(reportlib.TAB)

	# 16. Ensembl ENSMUSG IDs (60)

	if ensemblID.has_key(key):
		fp.write(string.join(ensemblID[key], ' '))
	else:
		fp.write(blankTag)
	fp.write(reportlib.TAB)

	# 17. VEGA OTTMUSG IDs (85)

	if vegaID.has_key(key):
		fp.write(string.join(vegaID[key], ' '))
	else:
		fp.write(blankTag)
	fp.write(reportlib.TAB)

	# 18. DFCI/TIGR IDs (35)

	if dfciID.has_key(key):
		fp.write(string.join(dfciID[key], ' '))
	else:
		fp.write(blankTag)
	fp.write(reportlib.TAB)

	# 19. DoTS IDs (36)

	if dotsID.has_key(key):
		fp.write(string.join(dotsID[key], ' '))
	else:
		fp.write(blankTag)
	fp.write(reportlib.TAB)

	# 20. NIA IDs (53)

	if niaID.has_key(key):
		fp.write(string.join(niaID[key], ' '))
	else:
		fp.write(blankTag)
	fp.write(reportlib.TAB)

	# 21. Unigene IDs (23)

	if unigeneID.has_key(key):
		fp.write(string.join(unigeneID[key], ' '))
	else:
		fp.write(blankTag)
	fp.write(reportlib.CRT)

reportlib.finish_nonps(fp)
