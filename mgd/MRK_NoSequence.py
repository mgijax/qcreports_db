#!/usr/local/bin/python

'''
#
# MRK_NoSequence.py 02/10/2003
#
# Report:
#       TR 4443
#
#	Genes with no nucleic or protein sequence assocations
#
#    		Gene Symbol
#		Ortholog Species
#		Ortholog LL ID
#		GXD Refs (total # of GXD Indexes to the Gene)
#		A&P Uses:  Y if the Gene has an MLC entry or Alleles
#			(excluding wild type alleles)
#		A&P Ref: primary reference of the Gene
#
# Usage:
#       MRK_NoSequence.py
#
# Notes:
#	- all reports use mgireport directory for output file
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
#
# lec	02/23/2004
#	- include XM (RefSeq)
#
# lec	01/29/2004
#	- exclude phenotypic mutants (TR 5139)
#
# lec	02/08/2003
#	- created
#
'''
 
import sys 
import os
import string
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

title = 'Genes with no Sequence Data (GenBank, SwissPROT, TrEMBL, RefSeq)'
fp = reportlib.init(sys.argv[0], title = title, outputdir = os.environ['QCREPORTOUTPUTDIR'])

fp.write(string.ljust('Gene Symbol', 27) + \
 	 string.ljust('GXD Refs', 12) + \
 	 string.ljust('A&P Uses?', 12) + \
 	 string.ljust('Primary Ref', 12) + \
 	 string.ljust('Ortholog LL Id', 42) + \
	 string.ljust('Orthology Species', 72) + \
 	 CRT)

fp.write('-' * 25 + '  ' + \
	 '-' * 10 + '  ' + \
	 '-' * 10 + '  ' + \
	 '-' * 10 + '  ' + \
	 '-' * 40 + '  ' + \
	 '-' * 70 + '  ' + CRT)

cmds = []

#
# select phenotypic mutant genes
#
cmds.append('select distinct m._Marker_key ' + \
'into #mutants ' + \
'from MRK_Marker m, ALL_ALlele a ' + \
'where m._Organism_key = 1 ' + \
'and m._Marker_Type_key = 1 ' + \
'and m._Marker_key = a._Marker_key ' + \
'and m.symbol = a.symbol ' + \
'and not exists (select 1 from MRK_Acc_View a ' + \
'where m._Marker_key = a._Object_key ' + \
'and a._LogicalDB_Key in (9, 13, 27, 41)) ')

#
# select Genes with no sequences
#
cmds.append('select m._Marker_key, m.symbol ' + \
'into #markers ' + \
'from MRK_Marker m ' + \
'where m._Organism_key = 1 ' + \
'and m._Marker_Type_key = 1 ' + \
'and m._Marker_Status_key in (1,3) ' + \
'and not exists (select 1 from MRK_Acc_View a ' + \
'where m._Marker_key = a._Object_key ' + \
'and a._LogicalDB_Key in (9, 13, 27, 41)) ' + \
'and not exists (select 1 from #mutants t where t._Marker_key = m._Marker_key)')

cmds.append('create nonclustered index idx_marker_key on #markers(_Marker_key)')

#
# select orthologs
#
cmds.append('select distinct m._Marker_key, orthologKey = m2._Marker_key, s.commonName ' + \
'into #orthologs ' + \
'from #markers m, HMD_Homology_Marker hm1, HMD_Homology_Marker hm2, MRK_Marker m2, MGI_Organism s ' + \
'where m._Marker_key = hm1._Marker_key ' + \
'and hm1._Homology_key = hm2._Homology_key ' + \
'and hm2._Marker_key = m2._Marker_key ' + \
'and m2._Organism_key != 1 ' + \
'and m2._Organism_key = s._Organism_key')

cmds.append('select * from #orthologs')

#
# select ll id of orthologs
#
cmds.append('select distinct o._Marker_key, a.accID ' + \
'from #orthologs o, MRK_Acc_View a ' + \
'where o.orthologKey = a._Object_key ' + \
'and a._LogicalDB_key = 24')

#
# select number of GXD index references for each marker
#
cmds.append('select m._Marker_key, gxd = count(i._Refs_key) ' + \
'from #markers m, GXD_Index i ' + \
'where m._Marker_key = i._Marker_key ' + \
'group by m._Marker_key')

#
# select whether there is MLC entry or Allele
# (excluding wild type allele)
#

cmds.append('select distinct m._Marker_key ' + \
'from #markers m ' + \
'where exists (select 1 from MLC_Text t where m._Marker_key = t._Marker_key) ' + \
'or exists (select 1 from ALL_Allele a where m._Marker_key = a._Marker_key ' + \
'and a.symbol not like "%<+>")')

#
# select primary references
#

cmds.append('select distinct m._Marker_key, b.accID ' + \
'from #markers m, MRK_History h, BIB_Acc_View b ' + \
'where m._Marker_key = h._Marker_key ' + \
'and h._Marker_key = h._History_key ' + \
'and h._Marker_Event_key = 1 ' + \
'and h._Refs_key = b._Object_key ' + \
'and b._LogicalDB_key = 1 ' + \
'and b.prefixPart = "J:"')

cmds.append('select * from #markers order by symbol')

results = db.sql(cmds, 'auto')

# store dictionary of orthologs
organism = {}
for r in results[4]:
	key = r['_Marker_key']
	value = r['commonName']
	if not organism.has_key(key):
		organism[key] = []
	organism[key].append(value)

# store dictionary of orthologs/ll ids
llids = {}
for r in results[5]:
	key = r['_Marker_key']
	value = r['accID']
	if not llids.has_key(key):
		llids[key] = []
	llids[key].append(value)

# store dictionary of gxd references
gxd = {}
for r in results[6]:
	key = r['_Marker_key']
	value = str(r['gxd'])
	gxd[key] = value

# store list of AP use values
ap = []
for r in results[7]:
	key = r['_Marker_key']
	ap.append(key)

# store dictionary of primary references
ref = {}
for r in results[8]:
	key = r['_Marker_key']
	value = r['accID']
	ref[key] = value

rows = 0
for r in results[-1]:
	key = r['_Marker_key']

	fp.write(string.ljust(r['symbol'], 27))

	if gxd.has_key(key):
		fp.write(string.ljust(gxd[key], 12))
	else:
		fp.write(string.ljust(' ' * 10, 12))

	if key in ap:
		fp.write(string.ljust("yes", 12))
	else:
		fp.write(string.ljust(' ' * 10, 12))

	if ref.has_key(key):
		fp.write(string.ljust(ref[key], 12))
	else:
		fp.write(string.ljust(' ' * 10, 12))

	if llids.has_key(key):
		fp.write(string.ljust(string.join(llids[key], ';'), 42))
	else:
		fp.write(string.ljust(' ' * 40, 42))

	if organism.has_key(key):
		fp.write(string.ljust(string.join(organism[key], ';'), 72))
	else:
		fp.write(string.ljust(' ' * 70, 72))

	fp.write(CRT)
	rows = rows + 1

fp.write('\n(%d rows affected)\n' % (rows))
reportlib.trailer(fp)
reportlib.finish_nonps(fp)	# non-postscript file

