#!/usr/local/bin/python

'''
#
# TR 3638/3639
#
# See TRs for report specifications.
#
# Fantom2 reports (QC and for RIKEN itself)
#
# QC Output files:
# 	1. FAN2_InvalidFinalMGIID.rpt
# 	2. FAN2_IncompleteCluster.rpt
# 	3. FAN2_MultRepClone.rpt
# 	4. FAN2_NoRepClone.rpt
# 	5. FAN2_NonRikenRepClone.rpt
# 	6. FAN2_DiscrRepClone.rpt
#
# RIKEN Output file:
#	7. fantom2.mgi
#
# Usage:
#       fantom2.py
#
# Used by:
#       Internal Fantom curators
#	RIKEN group (fantom2.mgi)
#
# Notes:
#
# History:
#
# lec	04/29/2002
#	- TR 3638, 3639
#
'''
 
import sys
import os
import string
import db
import reportlib

TAB = reportlib.TAB
CRT = reportlib.CRT

def excluded_clusters():

	#
	# the set of cluster ids excluded from the fantom2.mgi
	# report because these cluster ids appear in the
	# qc reports.
	#

	global cmds

	cmds.append('select distinct riken_cluster ' + \
		'into #excluded_cluster ' + \
		'from #invalidmgiID ' + \
		'union ' + \
		'select distinct riken_cluster ' + \
		'from #incomplete_cluster ' + \
		'union ' + \
		'select distinct riken_cluster ' + \
		'from #mult_rep ' + \
		'union ' + \
		'select distinct riken_cluster ' + \
		'from #no_rep_clone ' + \
		'union ' + \
		'select distinct riken_cluster ' + \
		'from #nonriken ' + \
		'union ' + \
		'select distinct riken_cluster ' + \
		'from #rep_discr ')

	cmds.append('create unique index index_cluster on #excluded_cluster(riken_cluster)')

def curated_clusters():

	#
	# the set of "curated" riken clones
	# determined by the presence of a final mgi ID
	# where the final mgi ID is like "MGI:" or is a riken clone
	#

	global cmds

	# the curated set of clones, by cluster 
	cmds.append('select distinct f1.riken_cluster ' + \
		'into #curated_cluster ' + \
		'from MGI_Fantom2 f1 ' + \
		'where f1.final_mgiID like "MGI:%" ' + \
		'and f1.riken_cloneid != "zilch" ' + \
		'or exists (select 1 from MGI_Fantom2 f2 ' + \
		'where f1.final_mgiID = f2.riken_cloneid ' + \
		'and f2.riken_cloneid != "zilch")')

	cmds.append('create unique index index_cluster on #curated_cluster(riken_cluster)')

	# results[0] and results[1]

def incomplete_cluster():

	#
	# the set of clusters which are members of the "curated" cluster
	# and which have no final mgi ID and no sequence quality
	#

	global cmds

	curated_clusters()

	# remove cluster = -1
	cmds.append('delete from #curated_cluster where riken_cluster = -1')
	
	cmds.append('select f1._Fantom2_key, f1.riken_cloneid, f1.riken_cluster ' + \
		'into #incomplete_cluster ' + \
		'from #curated_cluster c, MGI_Fantom2 f1 ' + 
		'where c.riken_cluster = f1.riken_cluster ' + \
		'and f1.final_mgiID in ("zilch", "zzilch") ' + \
		'and f1.seq_quality = "zilch" ')

	cmds.append('create index index_key on #incomplete_cluster(_Fantom2_key)')

	# results[5]
	cmds.append('select f1.riken_cloneid, f1.riken_cluster ' + \
		'from #incomplete_cluster c, MGI_Fantom2 f1 ' + 
		'where c._Fantom2_key = f1._Fantom2_key ' + \
		'order by f1.riken_cluster')

def invalid_finalmgiID():

	#
	# the set of clones where the final MGI id is an invalid clone id
	#

	global cmds

	cmds.append('select distinct f1._Fantom2_key, f1.riken_cloneid, f1.riken_cluster ' + \
		'into #invalidmgiID ' + \
		'from MGI_Fantom2 f1 ' + \
		'where f1.final_mgiID != "zilch" ' + \
		'and f1.final_mgiID != "zzilch" ' + \
		'and f1.final_mgiID not like "MGI:%" ' + \
		'and not exists (select 1 from MGI_Fantom2 f2 ' + \
		'where f1.final_mgiID = f2.riken_cloneid)')

	cmds.append('create index index_key on #invalidmgiID(_Fantom2_key)')

	# results[8]
	cmds.append('select f1.riken_cloneid, f1.riken_cluster, f1.final_mgiID ' + \
		'from #invalidmgiID c, MGI_Fantom2 f1 ' + \
		'where c._Fantom2_key = f1._Fantom2_key ' + \
		'order by f1.final_mgiID')

def multiple_representative():

	#
	# the set of clones, grouped by final MGI ID, which have more than one representative clone
	#

	global cmds

	cmds.append('select f1._Fantom2_key, f1.riken_cloneid, f1.final_mgiID, ' + \
		'f1.genbank_id, f1.riken_cluster ' + \
		'into #rep2 ' + \
		'from MGI_Fantom2 f1 ' + \
		'where f1.seq_note = "Representative" ' + \
		'and f1.final_mgiID not in ("zilch", "zzilch")')

	cmds.append('select * into #mult_rep from #rep2 group by final_mgiID having count(*) > 1')
	cmds.append('create index index_key on #mult_rep(_Fantom2_key)')

	# results[12]
	cmds.append('select * from #mult_rep order by final_mgiID')

def no_rep_clone():

	#
	# the set of curated clones (excluding singletons) which have a final mgi ID of "MGI:"
	# and no representative clone has been designated
	#

	global cmds

	cmds.append('select distinct f1._Fantom2_key, f1.final_mgiID, ' + \
		'f1.riken_cloneid, f1.riken_cluster ' + \
		'into #curated ' + \
		'from MGI_Fantom2 f1 ' + \
		'where f1.final_mgiID like "MGI:%" ' + \
		'and f1.riken_cloneid != "zilch" ' + \
		'or exists (select 1 from MGI_Fantom2 f2 ' + \
		'where f1.final_mgiID = f2.riken_cloneid ' + \
		'and f2.riken_cloneid != "zilch")')

	cmds.append('create index index_cluster on #curated(riken_cloneid)')
	cmds.append('delete from #curated where riken_cloneid = "zilch"')

	cmds.append('select * into #singleton from #curated group by final_mgiID having count(*) = 1')
	cmds.append('create index index_cluster on #singleton(riken_cloneid)')

	cmds.append('select c.* ' + \
		'into #no_rep_clone ' + \
		'from #curated c ' + \
		'where not exists (select 1 from MGI_Fantom2 f1 ' + \
		'where c.final_mgiID = f1.final_mgiID ' + \
		'and f1.seq_note = "Representative") ' + \
		'and not exists (select 1 from #singleton s ' + \
		'where c.riken_cloneid = s.riken_cloneid)')

	cmds.append('create index index_key on #no_rep_clone(_Fantom2_key)')

	# results[20]
	cmds.append('select * from #no_rep_clone order by final_mgiID')

def nonriken_rep_clone():
	
	#
	# the set of curated clones where the representative clone is a non-riken clone
	#

	global cmds

	cmds.append('select f1.riken_cluster, f1.riken_seqid, f1.final_mgiID ' + \
		'into #rep3 ' + \
		'from MGI_Fantom2 f1 ' + \
		'where f1.seq_note = "Representative" ' + \
		'and f1.final_mgiID not in ("zilch", "zzilch")')

	cmds.append('select * into #nondups from #rep3 group by final_mgiID having count(*) = 1')

	cmds.append('select * into #nonriken from #nondups where riken_seqid = -1')

	cmds.append('create index index_key on #nonriken(riken_cluster)')

	# results[25]
	cmds.append('select f1.final_mgiID, f1.genbank_id, f1.unigene_id, f1.tiger_tc ' + \
	            'from #nonriken n, MGI_Fantom2 f1 ' + \
		    'where n.final_mgiID = f1.final_mgiID ' + \
		    'order by final_mgiID')

def rep_discrepency():

	#
	# the set of representative clones where the final MGI ID is a RIKEN clone
	# and the final MGI ID != the record's RIKEN clone ID
	#

	global cmds

	cmds.append('select f1._Fantom2_key, f1.riken_cloneid, f1.final_mgiID, f1.riken_cluster, f1.seq_note ' + \
		'into #rep4 ' + \
		'from MGI_Fantom2 f1 ' + \
		'where f1.seq_note = "Representative" ' + \
		'and f1.final_mgiID not in ("zilch", "zzilch")')

	cmds.append('select * into #nondups4 from #rep4 group by final_mgiID having count(*) = 1')

	cmds.append('select * ' + \
		'into #rep_discr ' + \
		'from #nondups4 ' + \
		'where final_mgiID not like "MGI:%" ' + \
		'and riken_cloneid != final_mgiID')

	cmds.append('create index index_key on #rep_discr(_Fantom2_key)')

	# results[30]
	cmds.append('select * from #rep_discr order by final_mgiID')

def riken():

	#
	# the set of curated clusters
	#

	global cmds

	# results[33]
	cmds.append('select f1._Fantom2_key, f2.note ' + \
		'from #curated_cluster c, MGI_Fantom2 f1, MGI_Fantom2Notes f2 ' + \
		'where c.riken_cluster = f1.riken_cluster ' + \
		'and not exists (select 1 from #excluded_cluster e ' + \
		'where f1.riken_cluster = e.riken_cluster) ' + \
		'and f1._Fantom2_key = f2._Fantom2_key ' + \
		'and f2.noteType = "C" ')

	# results[34]
	cmds.append('select f1._Fantom2_key, f1.riken_seqid, f1.riken_cloneid, ' + \
		'f1.riken_cluster, f1.final_mgiID, ' + \
		'f1.seq_quality, f1.seq_note ' + \
		'from #curated_cluster c, MGI_Fantom2 f1 ' + \
		'where c.riken_cluster = f1.riken_cluster ' + \
		'and not exists (select 1 from #excluded_cluster e ' + \
		'where f1.riken_cluster = e.riken_cluster) ' + \
		'order by f1.final_mgiID, f1.riken_cluster')

def incomplete_cluster_report():

	fp = reportlib.init('FAN2_IncompleteCluster', outputdir = os.environ['QCREPORTOUTPUTDIR'], printHeading = 0)

	for r in results[5]:
		fp.write(r['riken_cloneid'] + TAB + \
			`r['riken_cluster']` + CRT)
	
	reportlib.finish_nonps(fp)

def invalid_finalmgiID_report():

	fp = reportlib.init('FAN2_InvalidFinalMGIID', outputdir = os.environ['QCREPORTOUTPUTDIR'], printHeading = 0)

	for r in results[8]:
		fp.write(r['riken_cloneid'] + TAB + \
			`r['riken_cluster']` + TAB + \
			r['final_mgiID'] + CRT)

	reportlib.finish_nonps(fp)

def multiple_representative_report():

	fp = reportlib.init('FAN2_MultRepClone', outputdir = os.environ['QCREPORTOUTPUTDIR'], printHeading = 0)

	for r in results[12]:
		fp.write(r['riken_cloneid'] + TAB + \
			r['genbank_id'] + TAB + \
			`r['riken_cluster']` + TAB + \
			r['final_mgiID'] + CRT)

	reportlib.finish_nonps(fp)

def no_rep_clone_report():

	fp = reportlib.init('FAN2_NoRepClone', outputdir = os.environ['QCREPORTOUTPUTDIR'], printHeading = 0)

	for r in results[20]:
		fp.write(r['riken_cloneid'] + TAB + \
			`r['riken_cluster']` + TAB + \
			r['final_mgiID'] + CRT)
	
	reportlib.finish_nonps(fp)

def nonriken_rep_clone_report():

	fp = reportlib.init('FAN2_NonRikenRepClone', outputdir = os.environ['QCREPORTOUTPUTDIR'], printHeading = 0)

	for r in results[25]:
		fp.write(r['genbank_id'] + TAB + \
			r['unigene_id'] + TAB + \
			r['tiger_tc'] + TAB + \
			r['final_mgiID'] + CRT)

	reportlib.finish_nonps(fp)

def rep_discrepency_report():

	fp = reportlib.init('FAN2_DiscrRepClone', outputdir = os.environ['QCREPORTOUTPUTDIR'], printHeading = 0)

	for r in results[30]:
		fp.write(r['riken_cloneid'] + TAB + \
			r['riken_cluster'] + TAB + \
			r['seq_note'] + TAB + \
			r['final_mgiID'] + CRT)
	
	reportlib.finish_nonps(fp)

def riken_report():

	fp = reportlib.init(sys.argv[0], fileExt = '.mgi', outputdir = os.environ['QCREPORTOUTPUTDIR'], printHeading = 0)

	notes = {}
	for r in results[33]:
		if not notes.has_key(r['_Fantom2_key']):
			notes[r['_Fantom2_key']] = r['note']
		else:
			newnote = notes[r['_Fantom2_key']] + r['note']
			notes[r['_Fantom2_key']] = newnote

	for r in results[34]:
		fp.write(`r['riken_seqid']` + TAB + \
			r['riken_cloneid'] + TAB + \
			`r['riken_cluster']` + TAB + \
			r['final_mgiID'] + TAB)

		if r['seq_quality'] != 'zilch':
			fp.write(r['seq_quality'])
		fp.write(TAB)
		
		if r['seq_note'] != 'zilch':
			fp.write(r['seq_note'])
		fp.write(TAB)

		if string.find(notes[r['_Fantom2_key']], 'Better RefSeq:UG') != -1:
			fp.write(notes[r['_Fantom2_key']])
		fp.write(TAB)

		fp.write(CRT)
		
	reportlib.finish_nonps(fp)

#
# Main
#

# use dbo login since the tables are read-protected
db.set_sqlUser(os.environ['DBOUSER'])
db.set_sqlPassword(string.strip(open(os.environ['DBOPASSWORDFILE'], 'r').readline()))

# initialize the queries
cmds = []
incomplete_cluster()
invalid_finalmgiID()
multiple_representative()
no_rep_clone()
nonriken_rep_clone()
rep_discrepency()
excluded_clusters()	# set of clusters to exlude from final riken report
riken()

# execute all of the queries
results = db.sql(cmds, 'auto')

# print the reports
incomplete_cluster_report()
invalid_finalmgiID_report()
multiple_representative_report()
no_rep_clone_report()
nonriken_rep_clone_report()
rep_discrepency_report()
riken_report()

