
'''
#
# VOC_InvalidProperties.py 10/17/2003
#
# Report:
#       Tab-delimited file
#	Annotation Properties that contain invalid terms
#
# Usage:
#       VOC_InvalidProperties.py
#
# Used by:
#       Annotation Editors
#
# History:
#
#
'''
 
import sys
import os
import reportlib
import db

db.setTrace()

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])
fp.write('\nInvalid "Properties" Values in GO Annotations; Terms of interest do not exist in MGI' + reportlib.CRT)
fp.write('\nTerms of interest:  CL, GO, MA, MGI' + 2 * reportlib.CRT)
rows = 0

#
# read in all term ids (13) of interest
# this is the list of valid accession ids
#
# 4: GO
# 6: Adult Mouse Anatomy
# 77: Protein Ontology
# 102: Cell Ontology
#
# and MGI: ids for markers
#

mgiLookup = []
results = db.sql('''
(
select a.accID from ACC_Accession a, VOC_Term t
where a._MGIType_key = 13 
and a._Object_key = t._Term_key
and t.isObsolete = 0
and t._Vocab_key in (4,6,77,102)
union all
select a.accID from ACC_Accession a where a._MGIType_key = 2 and a.prefixPart = 'MGI:' and a.preferred = 1
)
order by accID
''', 'auto')
for r in results:
    mgiLookup.append(r['accID'])

# read in all annotations that contains terms of interest

db.sql('''
        select distinct p.value, aa.accID, m.symbol, u.login
        into temporary table annotations 
        from VOC_Annot a, VOC_Evidence e, VOC_Evidence_Property p, VOC_Term t,
                ACC_Accession aa, MRK_Marker m, MGI_User u
        where a._AnnotType_key = 1000 
        and a._Annot_key = e._Annot_key 
        and e._AnnotEvidence_key = p._AnnotEvidence_key
        and p._PropertyTerm_key = t._Term_key
        and t._Vocab_key = 82
        and t.term not in (
                'anatomy', 
                'cell type', 
                'dual-taxon ID', 
                'evidence', 
                'external ref', 
                'gene product', 
                'modification', 
                'target', 
                'text')
        and p.value is not null 
        and (
             p.value like '%CL:%'
             or p.value like '%GO:%'
             or p.value like '%MA:%'
             or p.value like '%MGI:%'
            )
        and a._Term_key = aa._Object_key 
        and aa._MGIType_key = 13  
        and aa.preferred = 1 
        and a._Object_key = m._Marker_key 
        and e._ModifiedBy_key = u._User_key
        order by p.value
        ''', None)

results = db.sql('select * from annotations', 'auto')

for r in results:
    ids = r['value']
    ids = ids.replace(' ', ';')
    ids = ids.upper()
    delimiter = ';'
    idList = str.split(ids, delimiter)

    for id in idList:
        if str.find(id, 'CL:') >= 0 \
           or str.find(id, 'GO:') >= 0 \
           or str.find(id, 'MA:') >= 0 \
           or str.find(id, 'MGI:') >= 0 :
                if id not in mgiLookup:
                        fp.write(r['accID'] + reportlib.TAB + \
                                r['symbol'] + reportlib.TAB + \
                                r['value'] + reportlib.TAB + \
                                r['login'] + reportlib.CRT)
                        rows = rows + 1 

fp.write('\n(%d rows affected)\n' % (rows))
reportlib.finish_nonps(fp)
