
'''
#
# BioRxiv articles and published articles with the same title
#
'''
 
import sys
import os
import db
import reportlib

#db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

# select all the BioRxiv articles
db.sql('''select title, _Refs_key 
into temporary table biorxiv 
from BIB_View 
where lower(journal) ='biorxiv'
''', None)

db.sql('create index idx1 on biorxiv(title)', None)

# find duplicate titles in other journals excluding any '.' period on the end 
db.sql('''
select x._Refs_key as bioRefsKey, bv._Refs_key as journalRefsKey 
into temporary table dupes 
from BIB_View bv, biorxiv x 
where lower(bv.journal) !='biorxiv' 
and bv.title = x.title 
union 
select x._Refs_key as bioRefsKey, bv._Refs_key as journalRefsKey 
from BIB_View bv, biorxiv x 
where lower(bv.journal) !='biorxiv' 
and TRIM( TRAILING '.' FROM bv.title) = x.title
''', None)

db.sql('create index idx2 on dupes(bioRefsKey)', None)
db.sql('create index idx3 on dupes(journalRefsKey)', None)

# add in the info needed for the report 
db.sql('''
select distinct d.JournalRefsKey, 
a1.accid as biorxivMGI, 
a2.accid as journalMGI, 
bv2.journal, 
bv1.title as biorxivTitle, 
bv2.title as journalTitle, 
bv1.authors as biorxivAuthors, 
bv2.authors as journalAuthors, 
bv1.creation_date as biorxivCreationDate, 
bv2.creation_date as journalCreationDate 
into temporary table dupeswithinfo 
from dupes d, BIB_View bv1, BIB_View bv2, ACC_Accession a1, ACC_Accession a2 
where d.bioRefsKey = bv1._Refs_key 
and d.journalRefsKey = bv2._Refs_key 
and d.bioRefsKey = a1._object_key 
and a1.preferred = 1 
and a1._MGIType_key = 1 
and a1._LogicalDB_key = 1 
and a1.prefixPart = 'MGI:' 
and d.journalRefsKey = a2._object_key 
and a2.preferred = 1 
and a2._MGIType_key = 1 
and a2._LogicalDB_key = 1 
and a2.prefixPart = 'MGI:' 
order by bv1.title
''', None)

db.sql('create index idx4 on dupeswithinfo(journalRefsKey)', None)

# create lookup of articles with 'MGI:BioRxiv_preprint_in_db' workflow tags 
db.sql('''
select wft._refs_key, t.term 
into temporary table refsbiorxivtag 
from bib_workflow_tag wft, voc_term t 
where wft._tag_key = t._term_key 
and wft._tag_key = 80525411 
''', None)

db.sql('create index idx5 on refsbiorxivtag(_refs_key)', None)

# report whether or not the article has MGI:BioRxiv_preprint_in_db workflow tag 
results = db.sql('''
select d.biorxivMGI, 
d.journalMGI, 
d.biorxivTitle,
d.journal, 
d.journalTitle,
d.biorxivAuthors,
d.journalAuthors,
r.term as biorxivTag 
from dupeswithinfo d left outer join refsbiorxivtag r on (d.journalRefsKey = r._refs_key )
''', 'auto')

for r in results:
        sys.stdout.write(r['biorxivMGI'] + TAB)
        sys.stdout.write(r['journalMGI'] + TAB)
        sys.stdout.write(r['biorxivTitle'] + TAB)
        sys.stdout.write(r['journal'] + TAB)
        sys.stdout.write(r['journalTitle'] + TAB)
        sys.stdout.write(r['biorxivAuthors'] + TAB)
        sys.stdout.write(r['journalAuthors'] + TAB)

        if (r['biorxivTag'] == None):
                sys.stdout.write(CRT)
        else:
                sys.stdout.write(r['biorxivTag'] + CRT)

sys.stdout.flush()

