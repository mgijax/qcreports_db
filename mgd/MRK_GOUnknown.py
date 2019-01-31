#!/usr/local/bin/python

'''
#
# MRK_GOUnknown.py 
# Report:
#
# Usage:
#       MRK_GOUnknown.py
#
# Notes:
#       - all reports use mgireport directory for output file
#       - all reports use db default of public login
#       - all reports use server/database default of environment
#       - use lowercase for all SQL commands (i.e. select not SELECT)
#       - all public SQL reports require the header and footer
#       - all private SQL reports require the header
#
# History:
#
# sc	11/03/17
#	TR12607 exclude cre transgene refs from GO QC 15 (14 after littriage release)
#
# sc    10/09/2017
#	converted from MRK_GOUnknown.sql
#	Add new column for curator tag
'''

import sys
import os
import string
import mgi_utils
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#
print "initializing"
fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

# lookup for curator tag
curTagDict = {}
results = db.sql('''select t._Refs_key, vt.term
        from BIB_Workflow_Tag t, VOC_Term vt
        where t._Tag_key = vt._Term_key
        and vt.term like 'MGI:curator_%' ''', 'auto')
for r in results:
        refsKey = r['_Refs_key']
        tag = r['term']
        if refsKey not in curTagDict:
            curTagDict[refsKey] = []
        curTagDict[refsKey].append(tag)

# refs keys with the GO:NotforGOUnknown tag
db.sql('''select s._Refs_key
        into temporary table exclude
	from BIB_Workflow_Status s, BIB_Workflow_Tag t
	where s._Group_key =  31576666
	and s._Refs_key = t._Refs_key
	and t._Tag_key = 35429720''', None)

# markers with allele subtype 'recombinase' to exclude
db.sql('''select a._Marker_key
    into temporary table recomb
    from ALL_Allele a, VOC_Annot va
    where a._Allele_key = va._Object_key
    and va._AnnotType_key = 1014 
    and va._Term_key = 11025588''', None)

db.sql('create index recomb_idx1 on recomb(_Marker_key)', None)

# GO Annotations to unknown terms 
# only include non-FANTOM references 
# and J: creation date >= Annotation creation date 
# ('GO:0008150', 'GO:0003674', 'GO:0005575')

db.sql('''select distinct substring(m.symbol,1,25) as symbol, m._Marker_key, r._Refs_key,
    substring(r.jnumID,1,20) as jnumID,
    substring(r.pubmedID,1,20) as pubmedID, 
    to_char(rr.creation_date, 'MM/dd/yyyy') as jnumDate,
    to_char(a.creation_date, 'MM/dd/yyyy') as annotDate
    INTO TEMPORARY TABLE temp1
    from MRK_Marker m, VOC_Annot a, MRK_Reference r, BIB_Refs rr
    where m._Organism_key = 1 
    and m._Marker_key = a._Object_key 
    and a._AnnotType_key = 1000 
    and a._Term_key in (1098,120,6113)
    and m._Marker_key = r._Marker_key
    and r.pubmedID not in ('11217851', '12466851', '14621295', '11125038', '12466854', '12466855', '12693553')
    and r._Refs_key = rr._Refs_key
    and rr.creation_date >= a.creation_date
    and not exists(select 1
	from recomb r
	where m._Marker_key = r._Marker_key)''', None)

db.sql('create index temp1_idx1 on temp1(_Marker_key)', None)

db.sql('create index temp1_idx2 on temp1(_Refs_key)', None)

#
# grab the marker accession ids
#
db.sql('''select t._Marker_key, t.symbol, t._Refs_key, t.jnumID, t.pubmedID, jnumDate, annotDate, 
        substring(ma.accID,1,20) as mgiID
    INTO TEMPORARY TABLE temp2
    from temp1 t, ACC_Accession ma
    where t._Marker_key = ma._Object_key 
    and ma._MGIType_key = 2 
    and ma.prefixPart = 'MGI:' 
    and ma._LogicalDB_key = 1 
    and ma.preferred = 1''', None)

db.sql('create index temp2_idx1 on temp2(_Marker_key)', None)

db.sql('create index temp2_idx2 on temp2(_Refs_key)', None)

#
# set DO yes/no flag
#
db.sql('''select distinct t._Marker_key, t.symbol
    INTO TEMPORARY TABLE diseaseontology
    from temp2 t, VOC_Annot va,
    GXD_AlleleGenotype agt, VOC_Term vt, ALL_Allele a
    where t._Marker_key = agt._Marker_key
    and va._AnnotType_key = 1020
    and va._Term_key = vt._Term_key
    and vt.isObsolete = 0
    and va._Qualifier_key in (1614158)
    and va._Object_key = agt._Genotype_key
    and agt._Allele_key = a._Allele_key
    and a._Allele_Status_key != 847112
    and a.isWildType != 1''', None)

db.sql('create index diseaseontology_idx1 on diseaseontology(_Marker_key)', None)

#
# grab the pubmed ids
# category 1: status='indexed' group='GO', not annotated to GO, 
#     status for groups A&P, QTL, GXD is 'rejected'
# category 2: status='indexed' or 'chosen' (31576673, 31576671), group='GO', 
#       not annotated to GO,
#	status for groups A&P and QTL other than 'rejected' or 'not routed'
#	not in category 1
# category 3: any GO annotations
#      

# category 1: 

db.sql('''select t._Refs_key, t._Marker_key, t.symbol, t.mgiID, t.jnumID, 
	t.pubmedID, t.jnumDate, t.annotDate, '1'::text as category
    INTO TEMPORARY TABLE temp3
    from temp2 t
    where exists (select 1 from BIB_Workflow_Status s
	    where t._Refs_key = s._Refs_key
	    and s._Group_key = 31576666
	    and s._Status_key in (31576673, 31576671) 
	    and s.isCurrent = 1)
    and not exists (select 1 from exclude e
	    where e._Refs_key = t._Refs_key) 
    and not exists (select 1 from BIB_Workflow_Status s
	    where t._Refs_key = s._Refs_key
	    and s._Group_key in (31576664, 31576668, 31576665) 
	    and s._Status_key in (31576670, 31576671, 31576673, 31576674)
	    and s.isCurrent = 1)
    and not exists (select 1 from VOC_Annot va, VOC_Evidence e
	    where va._AnnotType_key = 1000
	    and va._Annot_key = e._Annot_key
	    and e._Refs_key = t._Refs_key)''', None)

# category 2: 

db.sql('''INSERT INTO temp3
select t._Refs_key, t._Marker_key, t.symbol, t.mgiID, t.jnumID, t.pubmedID, t.jnumDate, 
	t.annotDate, '2'::text as category
    from temp2 t
    where not exists (select 1 from temp3 t3 
	    where t.symbol = t3.symbol
	    and t.pubmedID = t3.pubmedID)
    and not exists (select 1 from exclude e
            where e._Refs_key = t._Refs_key)
    and exists (select 1 from BIB_Workflow_Status s
	    where t._Refs_key = s._Refs_key
	    and s._Group_key = 31576666
	    and s._Status_key in (31576673,31576671) 
	    and s.isCurrent = 1)
    and exists (select 1 from BIB_Workflow_Status s
	    where t._Refs_key = s._Refs_key
	    and s._Group_key in (31576664, 31576668)
	    and s._Status_key in (31576670,31576671, 31576673, 31576674)
	    and s.isCurrent = 1)
    and not exists (select 1 from VOC_Annot va, VOC_Evidence e
	    where va._AnnotType_key = 1000
	    and va._Annot_key = e._Annot_key
	    and e._Refs_key = t._Refs_key)''', None)

# category 3: any GO annotations 

db.sql('''INSERT INTO temp3
select t._Refs_key, t._Marker_key, t.symbol, t.mgiID, t.jnumID, t.pubmedID, t.jnumDate, 
	t.annotDate, '3'::text as category
    from temp2 t
    where not exists (select 1 from temp3 t3 
	    where t.symbol = t3.symbol
	    and t.pubmedID = t3.pubmedID)
    and not exists (select 1 from exclude e
            where e._Refs_key = t._Refs_key)
    and exists (select 1 from BIB_Workflow_Status s
	    where t._Refs_key = s._Refs_key
	    and s._Group_key = 31576666
	    and s._Status_key in (31576673,31576671) 
	    and s.isCurrent = 1)
    and not exists (select 1 from VOC_Annot va, VOC_Evidence e
	    where va._AnnotType_key = 1000
	    and va._Annot_key = e._Annot_key
	    and e._Refs_key = t._Refs_key)''', None)

db.sql('create index temp3_idx1 on temp3(_Marker_key)', None)

#
# set hasDO
#
db.sql('''select t.*, 'Y'::text as hasDO
    INTO TEMPORARY TABLE temp4
    from temp3 t
    where exists (select 1 from diseaseontology o
	where t._Marker_key = o._Marker_key)''', None)

db.sql('''INSERT INTO temp4
    select t.*, 'N'::text as hasDO
    from temp3 t
    where not exists (select 1 from diseaseontology o where t._Marker_key = o._Marker_key)''', None)

db.sql('create index temp4_idx1 on temp4(symbol)', None)

db.sql('create index temp4_idx2 on temp4(category)', None)

fp.write( 'All genes with ''unknown'' annotations with new indexed literature\n')
fp.write('J: creation date >= Annotation creation date)\n')
fp.write("and if reference is 'chosen' or 'indexed' for GO and ''not used''\n")
fp.write('for any GO annotation\n')
fp.write('(excludes FANTOM papers 11217851 and 12466851, and 14621295, 11125038, 12466854, 12466855, and 12693553)\n')
fp.write('(excludes markers with alleles of subtype "Recombinase")\n\n')

results = db.sql('''select count(distinct mgiID) as ct from temp4''', 'auto')
for r in results:
    fp.write('Number of unique MGI Gene IDs: \t\t\t\t%s\n' % r['ct'])

results = db.sql('''select  count(distinct mgiID)  as ct from temp4 where hasDO = 'Y' ''', 'auto')
for r in results:
    fp.write('Number of unique MGI Gene IDs associated with DO:\t%s\n' % r['ct'])

results = db.sql('''select count(*) as ct from temp4''', 'auto')
for r in results:
    fp.write('Number of total rows: \t\t\t\t\t%s\n' %  r['ct'])
fp.write('\n\n')

fp.write('Category 1 = chosen or indexed only for GO\n')
fp.write('Category 2 = chosen or indexed only for GO & A&P\n')
fp.write('Category 3 = chosen or indexed for GO and any other group\n\n')

fp.write(string.ljust('symbol', 25))
fp.write(string.ljust('mgiID', 15))
fp.write(string.ljust('jnumID', 15))
fp.write(string.ljust('pubmedID', 15))
fp.write(string.center('category', 10))
fp.write(string.center('hasDO', 10))
fp.write(string.ljust('jnumDate', 14))
fp.write(string.ljust('annotDate', 14))
fp.write(string.ljust('MGI Curator Tag', 50) + CRT*2)

results = db.sql('''select distinct _Refs_key, symbol, mgiID, jnumID, pubmedID, 
    category, hasDO, jnumDate, annotDate
    from temp4 
    order by symbol, category''', 'auto')
for r in results:
    refsKey = r['_Refs_key']

    # curator tags in MGI
    cur = ''
    if refsKey in curTagDict:
            curList = curTagDict[refsKey]
            cur = string.join(curList, ', ')

    fp.write('%s%s%s%s%s%s%s%s%s%s' % (string.ljust(r['symbol'], 25), string.ljust(r['mgiID'], 15), string.ljust(r['jnumID'], 15), string.ljust(r['pubmedID'], 15), string.center(r['category'], 10), string.center(r['hasDO'], 10), string.ljust(r['jnumDate'], 14), string.ljust(r['annotDate'], 14), string.ljust(cur, 50), CRT))
