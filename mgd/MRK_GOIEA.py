'''
#
# Report:
#
# 1/A: J# : group = GO, stauts = (Chosen, Indexed), exclude workflow tag = 'GO:QC5_IEA-only_exclude'
# 2/B: pubmed id : not null
# 3/C: ref in GXD? : group = GXD, status in (Chosen, Indexed, Full-coded)
# 4/D: mgi id
# 5/E: feature type(s)
# 6/F: symbol
# 7/G: name
# 8/H: DO associations term
#      DO/J: if group = GO, status not in (Full-coded, Rejected)
#      OR exclude workflow tag = 'GO:IEA-only_exclude'
# 9/J: Curator Tag
#
# History:
#
# 04/22/2021    lec
#       WTS2-568/changes to GO QC/MRK_GOIEA.py (TR13463)
#
'''
 
import sys 
import os
import reportlib
import db

db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], isHTML = 1)

fp.write('''
marker type = 'gene'
name not like 'gene model'
symbol not like '[A-Z][0-9][0-9][0-9][0-9][0-9]'
symbol not like '[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]'
symbol not like 'Gt(ROSA)26Sor'
symbol not like 'ORF'

''')

pdfurl = os.environ['PDFVIEWER_URL']
url = ''
results = db.sql('select url from ACC_ActualDB where _LogicalDB_key = 29', 'auto')
for r in results:
        url = r['url']

# markers with GO Annotations/IEA *only*
db.sql('''
        select m._Marker_key, m.symbol, m.name, a.accid as markerid
        into temporary table markers
        from MRK_Marker m, ACC_Accession a
        where m._Marker_Type_key = 1
        and m._Marker_Status_key = 1
        and m.name !~ 'gene model %'
        and m.symbol !~ '[A-Z][0-9][0-9][0-9][0-9][0-9]'
        and m.symbol !~ '[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]'
        and m.symbol !~ 'Gt(ROSA)26Sor'
        and m.symbol !~ 'ORF%'
        and m._Marker_key = a._Object_key
        and a._MGIType_key = 2
        and a._LogicalDB_key = 1
        and a.prefixPart = 'MGI:'
        and a.preferred = 1
        and exists (select 1 from  VOC_Annot a, VOC_Evidence e
                where m._Marker_key = a._Object_key
                and a._AnnotType_key = 1000
                and a._Annot_key = e._Annot_key
                and e._EvidenceTerm_key = 115)
        and not exists (select 1 from  VOC_Annot a, VOC_Evidence e
                where m._Marker_key = a._Object_key
                and a._AnnotType_key = 1000
                and a._Annot_key = e._Annot_key
                and e._EvidenceTerm_key != 115) 
        ''', None)
db.sql('create index markers_idx1 on markers(_Marker_key)', None)

# 1/A:  J# : exclude workflow tag = 'GO:IEA-only_exclude'
db.sql('''
        select distinct m.*, c._Refs_key, c.mgiid, c.pubmedid, c.jnumid, c.numericpart
        into temporary table refs
        from markers m , MRK_Reference r, BIB_Citation_Cache c
        where m._Marker_key = r._Marker_key
        and r._Refs_key = c._Refs_key
        and not exists (select 1 from BIB_Workflow_Tag t
                where r._Refs_key = t._Refs_key
                and t._Tag_key = 71460412
                )
        and exists (select 1 from BIB_Workflow_Status s
                where r._Refs_key = s._Refs_key
                and s.isCurrent = 1
                and s._Group_key = 31576666
                and s._Status_key in (31576671, 31576673)
        )
        ''', None)
db.sql('create index index_refs1_key on refs(_Refs_key)', None)

# 3/C:  ref in GXD? : group = GXD, status in (Chosen, Indexed, Full-coded)
results = db.sql('''
        select distinct r._Refs_key
        from refs r, BIB_Workflow_Status s
        where r._Refs_key = s._Refs_key
        and s._Group_key = 31576665
        and s._Status_key in (31576673, 31576671, 31576674)
        and s.isCurrent = 1
        ''', 'auto')
hasGxd = []
for r in results:
        hasGxd.append(r['_Refs_key'])

# 5/E:  feature type(s)
results = db.sql('''
        select distinct m._Marker_key, c.directterms
        from markers m, MRK_MCV_Cache c
        where m._Marker_key = c._Marker_key
        and c.qualifier = 'I'
        ''', 'auto')
featureLookup = {}
for r in results:
        key = r['_Marker_key']
        value = r['directterms']
        if key not in featureLookup:
                featureLookup[key] = []
        featureLookup[key].append(value)

# 8/H:  DO associations
results = db.sql('''
        select distinct r._Marker_key, d.term
        from refs r, MRK_DO_Cache d, BIB_Citation_Cache c
        where r._Marker_key = d._Marker_key
        and d._Refs_key = c._Refs_key
        ''', 'auto')
doLookup = {}
for r in results:
        key = r['_Marker_key']
        value = r['term']
        if key not in doLookup:
                doLookup[key] = []
        doLookup[key].append(value)

# 8/H:  J#s
#         DO/J: if group = GO, status not in (Full-coded, Rejected)
#         OR exclude workflow tag = 'GO:IEA-only_exclude'
results = db.sql('''
        select distinct r._Marker_key, c.jnumid
        from refs r, MRK_DO_Cache d, BIB_Citation_Cache c
        where r._Marker_key = d._Marker_key
        and d._Refs_key = c._Refs_key
        and not exists (select 1 from BIB_Workflow_Status s
                where d._Refs_key = s._Refs_key
                and s.isCurrent = 1
                and s._Group_key = 31576666
                and s._Status_key in (31576674,31576672)
        )
        union 
        select distinct r._Marker_key, c.jnumid
        from refs r, MRK_DO_Cache d, BIB_Citation_Cache c
        where r._Marker_key = d._Marker_key
        and d._Refs_key = c._Refs_key
        and exists (select 1 from BIB_Workflow_Tag t
                where r._Refs_key = t._Refs_key
                and t._Tag_key = 71460412
                )
        ''', 'auto')
doRefsLookup = {}
for r in results:
        key = r['_Marker_key']
        value = r['jnumid']
        if key not in doRefsLookup:
                doRefsLookup[key] = []
        doRefsLookup[key].append(value)
#print(doRefsLookup)

#
#9/J: Curator Tag
#
results = db.sql('''
        select distinct r._Refs_key, t.term
        from refs r, BIB_Workflow_Tag tg, VOC_Term t
        where r._Refs_key = tg._Refs_key
        and tg._Tag_key = t._Term_key
        and t.term like 'GO:IP_%'
        ''', 'auto')
tagLookup = {}
for r in results:
        key = r['_Refs_key']
        value = r['term']
        if key not in tagLookup:
                tagLookup[key] = []
        tagLookup[key].append(value)
#print(tagLookup)

# final select
#

results = db.sql('select distinct _marker_key from refs', 'auto')
fp.write('\nNumber of unique Markers: ' + str(len(results)))
results = db.sql('select distinct _refs_key from refs', 'auto')
fp.write('\nNumber of unique GO References: ' + str(len(results)))
results = db.sql(' select * from refs order by symbol, numericpart ', 'auto')
fp.write('\nNumber of rows: ' + str(len(results)))
fp.write('\n\n')

fp.write('\nJ# pubmed ID\tref in GXD?\tmgi ID\tfeature type\tsymbol\tname\tDO [J#]\tCurator tag\n\n')

for r in results:

        refKey = r['_Refs_key']
        markerKey = r['_Marker_key']

        fp.write('<A HREF="%s%s">%s</A>' %(pdfurl, r['mgiid'], r['jnumid']) + TAB)

        if r['pubmedid'] != None:
           purl = str.replace(url, '@@@@', r['pubmedid'])
           fp.write('<A HREF="%s">%s</A>' % (purl, r['pubmedid']))
        fp.write(TAB)

        if refKey in hasGxd:
                fp.write('Y' + TAB)
        else:
                fp.write('N' + TAB)

        fp.write(r['markerid'] + TAB)

        if markerKey in featureLookup:
                fp.write('|'.join(featureLookup[markerKey]))
        fp.write(TAB)

        fp.write('<A HREF="http://www.informatics.jax.org/marker/%s">%s</A>' % (r['markerid'], r['symbol']) + TAB)

        fp.write(r['name'] + TAB)

        if markerKey in doLookup:
                fp.write('DO')

        if markerKey in doRefsLookup:
                fp.write('-' + '|'.join(doRefsLookup[markerKey]))
        fp.write(TAB)

        if refKey in tagLookup:
                fp.write('|'.join(tagLookup[refKey]))
        fp.write(CRT)

reportlib.finish_nonps(fp, isHTML = 1)	# non-postscript file

