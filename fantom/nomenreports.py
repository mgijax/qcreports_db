#!/usr/local/bin/python

'''
#
# TR 3863 - Nomen reports for Fantom2
#
# See TR for report specifications.
#
# Usage:
#       ambiguousmerge1.py
#
# Used by:
#       Internal Fantom curators
#
# Notes:
#
# History:
#
# lec	07/03/2002
#	- TR 3863
#
'''
 
import sys
import os
import string
import db
import reportlib
import mgi_utils

TAB = reportlib.TAB
CRT = reportlib.CRT

reportdir = '/mgi/all/wts_projects/3800/3863'

cmds = []
nnotes = {}
cnotes = {}

def select_notes():
	
	global cmds

	# nomenclature notes
	cmds.append('select n._Fantom2_key, n.note ' + \
		'from #fantom2 f1, MGI_Fantom2Notes n ' + \
		'where f1._Fantom2_key = n._Fantom2_key ' + \
		'and n.noteType = "N" ' + \
		'order by n._Fantom2_key, n.sequenceNum')

	# curator notes
	cmds.append('select n._Fantom2_key, n.note ' + \
		'from #fantom2 f1, MGI_Fantom2Notes n ' + \
		'where f1._Fantom2_key = n._Fantom2_key ' + \
		'and n.noteType = "C" ' + \
		'order by n._Fantom2_key, n.sequenceNum')

def select_records(orderBy):

	global cmds

	cmds.append('select f._Fantom2_key, f.riken_cloneid, f.genbank_id, f.riken_cluster, ' + \
		'c.gba_mgiID, f.final_mgiID, ' + \
		'f.final_symbol1, f.final_name1, f.final_symbol2, f.final_name2, ' + \
		'f.seq_note, f.seq_quality, f.nomen_event, f.modifiedBy ' + \
		'from #fantom2 f1, MGI_Fantom2 f, MGI_Fantom2Cache c ' + \
		'where f1._Fantom2_key = f._Fantom2_key ' + \
		'and f._Fantom2_key = c._Fantom2_key ' + \
		'order by %s' % (orderBy))

def process_nnotes(r):

	global nnotes

	if not nnotes.has_key(r['_Fantom2_key']):
		nnotes[r['_Fantom2_key']] = []
	nnotes[r['_Fantom2_key']].append(string.strip(r['note']))

def process_cnotes(r):

	global cnotes

	if not cnotes.has_key(r['_Fantom2_key']):
		cnotes[r['_Fantom2_key']] = []
	cnotes[r['_Fantom2_key']].append(string.strip(r['note']))

def process_records(r):

	fp.write(r['riken_cloneid'] + TAB + \
		r['genbank_id'] + TAB + \
		`r['riken_cluster']` + TAB + \
		r['gba_mgiID'] + TAB + \
		r['final_mgiID'] + TAB + \
		r['final_symbol1'] + TAB + \
		r['final_name1'] + TAB + \
		r['final_symbol2'] + TAB + \
		r['final_name2'] + TAB + \
		r['seq_note'] + TAB + \
		r['seq_quality'] + TAB + \
		r['nomen_event'] + TAB)

	if nnotes.has_key(r['_Fantom2_key']):
		fp.write(string.join(nnotes[r['_Fantom2_key']], ''))
	fp.write(TAB)

	if cnotes.has_key(r['_Fantom2_key']):
		fp.write(string.join(cnotes[r['_Fantom2_key']], ''))
	fp.write(TAB)

	fp.write(r['modifiedBy'] + CRT)

def do_all(extra = 0, orderBy = 'f.final_mgiID'):

	cmds.append('create nonclustered index idx_key on #fantom2(_Fantom2_key)')

	select_notes()
	select_records(orderBy)

	parsers = []
	parsers.append(None)
	parsers.append(None)

	for i in range(extra):
		parsers.append(None)

	parsers.append(process_nnotes)
	parsers.append(process_cnotes)
	parsers.append(process_records)
	db.sql(cmds, parsers)
	reportlib.finish_nonps(fp)

def ambiguous_merge1():

	global cmds, fp

	fp = reportlib.init('Ambiguous_Merge_1', outputdir = reportdir, printHeading = 0)

	cmds = []

	cmds.append('select f._Fantom2_key ' + \
		'into #fantom2 ' + \
		'from MGI_Fantom2 f, MGI_Fantom2Cache c ' + \
		'where f.nomen_event = "Merge" ' + \
		'and f._Fantom2_key = c._Fantom2_key ' + \
		'and f.final_mgiID = c.gba_mgiID ')

	do_all()

def ambiguous_merge2():

	global cmds, fp

	fp = reportlib.init('Ambiguous_Merge_2', outputdir = reportdir, printHeading = 0)

	cmds = []

	cmds.append('select f._Fantom2_key ' + \
        	'into #fantom2 ' + \
        	'from MGI_Fantom2 f ' + \
        	'where f.nomen_event = "Merge" ' + \
        	'and f.final_mgiID not like "MGI:%" ' + \
        	'union ' + \
        	'select f._Fantom2_key ' + \
        	'from MGI_Fantom2 f ' + \
        	'where f.nomen_event = "Merge" ' + \
        	'and f.final_mgiID like "MGI:%" ' + \
        	'and not exists (select 1 from MRK_Acc_View a ' + \
        	'where f.final_mgiID = a.accID)')

	do_all()

def ambiguous_merge3():

	global cmds, fp

	fp = reportlib.init('Ambiguous_Merge_3', outputdir = reportdir, printHeading = 0)

	cmds = []

	# merge events
	cmds.append('select distinct final_mgiID into #f1 from MGI_Fantom2 ' + \
		'where nomen_event = "Merge" and final_mgiID like "MGI:%"')

	cmds.append('create nonclustered index idx_key on #f1(final_mgiID)')

	# all final_mgiIDs and gba_mgiIDs for records which match the final_mgiID from previous query
	cmds.append('select f._Fantom2_key, f.final_mgiID, c.gba_mgiID ' + \
        	'into #f2 ' + \
        	'from #f1 a, MGI_Fantom2 f, MGI_Fantom2Cache c ' + \
		'where a.final_mgiID = f.final_mgiID ' + \
        	'and f._Fantom2_key = c._fantom2_key ')

	# all records with the same final_mgiID and all gba_mgiIDs are zilch
	cmds.append('select f1._Fantom2_key, f1.final_mgiID, f1.gba_mgiID ' + \
		'into #fantom2 ' + \
		'from #f2 f1 ' + \
        	'where not exists (select 1 from #f2 f2 ' + \
        	'where f1.final_mgiID = f2.final_mgiID ' + \
        	'and f2.gba_mgiID != "zilch")')

	do_all(extra = 3)

def ambiguous_rename():

	global cmds, fp

	fp = reportlib.init('Ambiguous_Rename', outputdir = reportdir, printHeading = 0)

	cmds = []

	# rename events
	cmds.append('select f._Fantom2_key ' + \
        	'into #fantom2 ' + \
        	'from MGI_Fantom2 f ' + \
        	'where f.nomen_event = "Rename" ' + \
        	'and (f.final_symbol2 = "zilch" or f.final_name2 = "zilch")')

	do_all()

def nomen_merge():

	global cmds, fp

	fp = reportlib.init('Nomen_Merge', outputdir = reportdir, printHeading = 0)

	cmds = []

	cmds.append('select f._Fantom2_key ' + \
        	'into #fantom2 ' + \
        	'from MGI_Fantom2 f, MGI_Fantom2Cache c ' + \
        	'where f._Fantom2_key = c._Fantom2_key ' + \
		'and f.final_mgiID != c.gba_mgiID ' + \
		'and f.final_mgiID like "MGI:%" ' + \
		'and c.gba_mgiID like "MGI:%" ' + \
        	'and exists (select 1 from MRK_Acc_View a ' + \
        	'where f.final_mgiID = a.accID) ' + \
        	'and exists (select 1 from MRK_Acc_View a ' + \
        	'where c.gba_mgiID = a.accID)')

	do_all()

def nomen_split_reassociate():

	global cmds, fp

	fp = reportlib.init('Nomen_SplitReassociate', outputdir = reportdir, printHeading = 0)

	cmds = []

	# split/reassociate OR final_mgiID = riken_cloneID and RA MGI ID is valid
	cmds.append('select f._Fantom2_key ' + \
        	'into #fantom2 ' + \
        	'from MGI_Fantom2 f ' + \
        	'where f.nomen_event in ("Split", "Reassociate") ' + \
		'union ' + \
		'select f._Fantom2_key ' + \
        	'from MGI_Fantom2 f, MGI_Fantom2Cache c ' + \
		'where f._Fantom2_key = c._Fantom2_key ' + \
		'and f.final_mgiID = f.riken_cloneid ' + \
		'and c.gba_mgiID like "MGI:%" ' + \
        	'and exists (select 1 from MRK_Acc_View a ' + \
        	'where c.gba_mgiID = a.accID)')

	do_all(orderBy = 'f.nomen_event, f.final_mgiID')

def nomen_rename():

	global cmds, fp

	fp = reportlib.init('Nomen_Rename', outputdir = reportdir, printHeading = 0)

	cmds = []

	cmds.append('select f._Fantom2_key ' + \
        	'into #fantom2 ' + \
        	'from MGI_Fantom2 f ' + \
        	'where f.final_symbol2 != "zilch" or f.final_name2 != "zilch"')

	do_all()

def nomen_probableortholog():

	global cmds, fp

	fp = reportlib.init('Nomen_ProbableOrtholog', outputdir = reportdir, printHeading = 0)

	cmds = []

	cmds.append('select f._Fantom2_key ' + \
        	'into #fantom2 ' + \
        	'from MGI_Fantom2 f, MGI_Fantom2Notes n ' + \
        	'where f._Fantom2_key = n._Fantom2_key ' + \
		'and n.noteType in ("C", "N") ' + \
		'and n.note like "%Probable Ortholog%"')

	do_all()

def nomen_possibleortholog():

	global cmds, fp

	fp = reportlib.init('Nomen_PossibleOrtholog', outputdir = reportdir, printHeading = 0)

	cmds = []

	cmds.append('select f._Fantom2_key ' + \
        	'into #fantom2 ' + \
        	'from MGI_Fantom2 f, MGI_Fantom2Notes n ' + \
        	'where f._Fantom2_key = n._Fantom2_key ' + \
		'and n.noteType in ("C", "N") ' + \
		'and n.note like "%Possible Ortholog%"')

	do_all()

def nomen_probableparalog():

	global cmds, fp

	fp = reportlib.init('Nomen_ProbableParalog', outputdir = reportdir, printHeading = 0)

	cmds = []

	cmds.append('select f._Fantom2_key ' + \
        	'into #fantom2 ' + \
        	'from MGI_Fantom2 f, MGI_Fantom2Notes n ' + \
        	'where f._Fantom2_key = n._Fantom2_key ' + \
		'and n.noteType in ("C", "N") ' + \
		'and n.note like "%Probable Paralog%"')

	do_all()

#
# Main
#

fp = None

# use dbo login since the tables are read-protected
db.set_sqlUser(os.environ['DBOUSER'])
db.set_sqlPassword(string.strip(open(os.environ['DBOPASSWORDFILE'], 'r').readline()))

#ambiguous_merge1()
#ambiguous_merge2()
ambiguous_merge3()
#ambiguous_rename()
#nomen_merge()
#nomen_split_reassociate()
#nomen_rename()
#nomen_probableortholog()
#nomen_possibleortholog()
#nomen_probableparalog()

