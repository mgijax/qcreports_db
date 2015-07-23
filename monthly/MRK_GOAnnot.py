#!/usr/local/bin/python

'''
#
# TR 10559
#
# Report:
#
# We would like a new QC report that lists markers of type = gene and the total 
# number of GO annotations associated with that gene.  Include only genes that 
# have GO annotations
# 
# Columns to appear:
# 
# 1) MGI ID of marker (Marker Type = gene)
# 
# 2) Marker feature-type ( ex: 'protein-coding gene' or 'whatever'
# 
# 3) Marker Symbol
# 
# 4) # of GO for for that gene
# 
# 5) # of GO annotations that are IPI, IGI, IDA, ISS, ISO, ISA, IMP
# 
# 6) # of papers in masterBib selected for GO but 'not used'. 
# 
# 7) # of papers in masterBib selected for GO but 'used'. 
# 
# Usage:
#       MRK_GOAnnot.py
#
# Notes:
#
# History:
#
# lec   10/22/2014
#       - TR11750/postres complient
#
# 01/31/2011	lec
#       - created; monthly report
#
'''
 
import sys 
import os 
import string
import reportlib
import db

db.setTrace()
db.setAutoTranslateBE()

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Total GO Annotations per Gene', os.environ['QCOUTPUTDIR'])

fp.write('includes:\n')
fp.write('    markers of type "gene"\n\n')
fp.write('field 1: MGI id\n')
fp.write('field 2: marker feature type\n')
fp.write('field 3: marker symbol\n')
fp.write('field 4: # of GO annotations for this gene\n')
fp.write('field 5: # of GO annotations that are IPI, IGI, IDA, ISS, ISO, ISA, IMP\n')
fp.write('field 6: # of papers selected for GO but "not used"\n')
fp.write('  . includes a reference even if it is "used" by another marker\n')
fp.write('field 7: # of papers selected for GO but "used"\n')
fp.write('  . excludes GO GAF loads (GOA, RGD, GO_Central, etc.)\n')
fp.write('  . excludes evidence codes IEA, ND\n')
fp.write('\n')

#
# markers with 
#   marker type 'gene'
#   contain GO annotations
#
db.sql('''
	select distinct m._Marker_key, m.symbol
	into #markers
        from MRK_Marker m
        where m._Marker_Type_key = 1
	and exists (select 1 from VOC_Annot a
	    where m._Marker_key = a._Object_key
	    and a._AnnotType_key = 1000)
       ''', None)
db.sql('create index idx1 on #markers(_Marker_key)', None)

# marker ids

mgiIDs = {}
results = db.sql('''select m._Marker_key, a.accID
	    from #markers m, ACC_Accession a 
	    where m._Marker_key = a._Object_key 
	    and a._LogicalDB_key = 1 
	    and a._MGIType_key = 2
	    and a.prefixPart = "MGI:"
	    and a.preferred = 1
	    ''', 'auto')
for r in results:
    key = r['_Marker_key']
    value = r['accID']
    mgiIDs[key] = value

#
# marker feature type
#
mgiFeature = {}
results = db.sql('''
	   select m._Marker_key, t.term
	   from #markers m, VOC_Annot a, VOC_Term t
	   where m._Marker_key = a._Object_key
	   and a._AnnotType_key = 1011
	   and a._Term_key = t._Term_key
	''', 'auto')
for r in results:
    key = r['_Marker_key']
    value = r['term']
    mgiFeature[key] = value

# 
# count of GO annotations
# grouped by marker
#
totalAnnot = {}
results = db.sql('''
	select m._Marker_key, 
	       count(distinct v._Annot_key) as totalAnnot
        from #markers m, VOC_Annot v
            where m._Marker_key = v._Object_key
            and v._AnnotType_key = 1000
	    group by m._Marker_key
       ''', 'auto')
for r in results:
    key = r['_Marker_key']
    totalAnnot[key] = r['totalAnnot']

# 
# count of GO annotations/IPI/IGI/IDA/ISS/ISO/ISA/IMP
# grouped by marker
#
totalEvi = {}
results = db.sql('''
	select m._Marker_key, 
	       count(distinct v._Annot_key) as totalEvi
        from #markers m, VOC_Annot v, VOC_Evidence e
            where m._Marker_key = v._Object_key
            and v._AnnotType_key = 1000
	    and v._Annot_key = e._Annot_key
	    and e._EvidenceTerm_key in (109,110,111,112,114,3251466,3251496)
	    group by m._Marker_key
       ''', 'auto')
for r in results:
    key = r['_Marker_key']
    totalEvi[key] = r['totalEvi']

#
# count of references by gene that are "not used"
#
# uses almost the same query as is used by EI GOVocAnnot module
#
# GO/EI excludes a Reference if it exists with another Marker/GO annotation
# however, this report will include that Reference
# 0610005C13Rik (count 1 in report, count 0 in GO EI) due to Wnk1/J:86696 
#
totalNotUsed = {}
results = db.sql('''
	select m._Marker_key, count(distinct r._Refs_key) as totalNotUsed
	from #markers m, BIB_GOXRef_View r
	where m._Marker_key = r._Marker_key
	and not exists (select 1 from VOC_Annot a, VOC_Evidence e
	where a._AnnotType_key = 1000
	and m._Marker_key = a._Object_key
	and a._Annot_key = e._Annot_key
	and e._Refs_key = r._Refs_key)
	group by m._Marker_key
     ''', 'auto')
for r in results:
    key = r['_Marker_key']
    value = r['totalNotUsed']
    totalNotUsed[key] = value

# count of references by gene that are "used"
# use same query as GO_stats.py:Curator=>
#   exclude GO GAF loads (GOA, RGD, etc.)
#   exclude evidence codes (IEA, ND)
totalUsed = {}
results = db.sql('''
	select m._Marker_key, count(distinct e._Refs_key) as totalUsed
	from #markers m, VOC_Annot a, VOC_Evidence e, MGI_User u
	where a._AnnotType_key = 1000
	and m._Marker_key = a._Object_key
	and a._Annot_key = e._Annot_key
	and e._Refs_key not in (74750, 61933,73199,73197)
	and e._EvidenceTerm_key not in (115,118)
	and e._CreatedBy_key = u._User_key
	and u.login not like ('GOA_%')
	and u.login not in ('GOC', 'GO_Central', 'UniProtKB')
	group by m._Marker_key
     ''', 'auto')
for r in results:
    key = r['_Marker_key']
    value = r['totalUsed']
    totalUsed[key] = value

# final output to print
results = db.sql('select distinct m._Marker_key, m.symbol from #markers m order by symbol', 'auto')

fp.write('total # of genes:  ' + str(len(results)) + 2*CRT)

for r in results:

    key = r['_Marker_key']

    fp.write(mgiIDs[key] + TAB)

    if mgiFeature.has_key(key):
      fp.write(mgiFeature[key])
    fp.write(TAB)

    fp.write(r['symbol'] + TAB)
    fp.write(str(totalAnnot[key]) + TAB)

    if totalEvi.has_key(key):
      fp.write(str(totalEvi[key]))
    else:
      fp.write('0')
    fp.write(TAB)

    if totalNotUsed.has_key(key):
      fp.write(str(totalNotUsed[key]))
    else:
      fp.write('0')
    fp.write(TAB)

    if totalUsed.has_key(key):
      fp.write(str(totalUsed[key]))
    else:
      fp.write('0')
    fp.write(CRT)

reportlib.finish_nonps(fp)

