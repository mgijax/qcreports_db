
'''
#
# QTL_Triage.py
#
# Report:
#       Weekly QTL Triage Report
#
#	Routed (R) or Chosen (C)
#	J:
#	Year
#	QTL symbol (if there is one)
#	Curator that Routed/Chose reference
#	QTL tags
#	
# Usage:
#       QTL_Triage.py
#
# lec	12/04/2017
#	- TR12730/changes per Deb Reed (djr)
#
# sc	10/06/2017
#	- Littriage project, update to use BIB_Workflow Status of 'routed'
#
# sc	08/31/2015
#	- TR12082 add markers
#
# sc   07/29/2015
#       - TR12082
#
'''
 
import sys 
import os
import mgi_utils
import reportlib
import Set
import db
import string

db.setTrace()
db.useOneConnection(1)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE
reportlib.column_width = 150

#
# Main
#

fp = reportlib.init(sys.argv[0], 'References with status "Routed or Chosen"', outputdir = os.environ['QCOUTPUTDIR'])
fp.write('Status,J:,Year,QTL symbol,Curator,QTL tags' + 2*CRT)

#
# reference in group QTL
# current status in ('Routed', 'Chosen')
# no Mapping records
#
db.sql('''
        select distinct r._Refs_key, t.term as status, c.mgiID, c.jnumID, r.year, u.login
        into temporary table qtl_refs
        from BIB_Refs r, BIB_Citation_Cache c, BIB_WorkFlow_Status wfs, VOC_Term t, MGI_User u
        where r._Refs_key = c._Refs_key
        and r._Refs_key = wfs._Refs_key
        and wfs._Group_key = 31576668
        and wfs._Status_key in (31576670,31576671)
        and wfs.isCurrent = 1
        and wfs._Status_key = t._Term_key
        and wfs._CreatedBy_key = u._User_key
        and not exists (select 1 from MLD_Expts e
                where r._Refs_key = e._Refs_key
                and e.exptType in ('TEXT', 'TEXT-QTL', 'TEXT-QTL-Candidate Genes', 'TEXT-Congenic', 'TEXT-Meta Analysis')
                )
        order by r.year desc, status, c.jnumID
        ''', None)

db.sql('create index idx1 on qtl_refs(_Refs_key)', None)

#
# has QTL: tags
#
tagLookup = {}
results = db.sql('''
                select r._Refs_key, t.term
                from qtl_refs r, BIB_Workflow_Tag wft, VOC_Term t
                where r._Refs_key = wft._Refs_key
                and wft._Tag_key = t._Term_key
                and t.term like 'QTL:%'
                order by r._Refs_key, t.term
                ''', 'auto')
for r in results:	
    key = r['_Refs_key']
    value = r['term']
    if key not in tagLookup:
        tagLookup[key] = []
    tagLookup[key].append(value)

#
# has QTL markers
#
markerLookup = {}
results = db.sql('''
                select r._Refs_key, m.symbol
                from qtl_refs r, MRK_Reference rm, MRK_Marker m
                where r._Refs_key = rm._Refs_key
                and rm._Marker_key = m._Marker_key
                and m._Marker_Type_key = 6
                ''', 'auto')
for r in results:	
    key = r['_Refs_key']
    value = r['symbol']
    if key not in markerLookup:
        markerLookup[key] = []
    markerLookup[key].append(value)

#
# Routed
#
results = db.sql('''select * from qtl_refs where status = 'Routed' ''', 'auto')
for r in results:
    key = r['_Refs_key']
    fp.write('R' + TAB)
    fp.write(r['mgiID'] + TAB)
    fp.write(str(r['jnumID']) + TAB)
    fp.write(str(r['year']) + TAB)
    if key in markerLookup:
        fp.write(';'.join(markerLookup[key]))
    fp.write(TAB)
    fp.write(r['login'] + TAB)
    if key in tagLookup:
        fp.write(';'.join(tagLookup[key]))
    fp.write(CRT)
fp.write('\n(%d rows affected)\n\n' % (len(results)))

#
# Chosen
#
results = db.sql('''select * from qtl_refs where status = 'Chosen' ''', 'auto')
for r in results:
    key = r['_Refs_key']
    fp.write('C' + TAB)
    fp.write(r['mgiID'] + TAB)
    fp.write(str(r['jnumID']) + TAB)
    fp.write(str(r['year']) + TAB)
    if key in markerLookup:
        fp.write(';'.join(markerLookup[key]))
    fp.write(TAB)
    fp.write(r['login'] + TAB)
    if key in tagLookup:
        fp.write(';'.join(tagLookup[key]))
    fp.write(CRT)
fp.write('\n(%d rows affected)\n\n' % (len(results)))

db.useOneConnection(0)
reportlib.finish_nonps(fp)	# non-postscript file
