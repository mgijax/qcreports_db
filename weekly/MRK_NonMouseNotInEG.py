'''
#
#
# Report:
#       Weekly report of Non-mouse Markers with Allele Relatonships and Marker is no longer in Entrez Gene
#
# History:
#
# lec   01/31/2023
#	- created https://mgi-jira.atlassian.net/browse/FL2-172
#
'''
 
import sys 
import os
import string
import reportlib
import db

db.useOneConnection(1)

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

fp = reportlib.init(sys.argv[0], '\tNon-Mouse Expressed Component/Driver Component whose Marker does not exist in EntrezGene', os.environ['QCOUTPUTDIR'])

fp.write('\norganisms used by non-mouse entrezgene load: cattle,chicken,chimpanzee,dog,human,macaque(rhesus),rat,frog(X. tropicalis),zebrafish\n\n')

fp.write('NCBI ID' + TAB)
fp.write('gene symbol' + TAB)
fp.write('organism (commonname)' + TAB)
fp.write('relationship type (expressed_component or driver_component)' + TAB)
fp.write('allele mgi id' + TAB)
fp.write('allele symbol' + CRT)

results = db.sql('''
(
select m._Marker_key, m._Organism_key, s.commonname, m.symbol as msymbol, a.symbol as asymbol, t.term as relationshipTerm, 
eg.accid as egID, aa.accid as alleleID
from MRK_Marker m, MGI_Organism s, MGI_Relationship r, ALL_Allele a, VOC_Term t, ACC_Accession eg, ACC_Accession aa
where m._Organism_key in (2,10,11,13,40,63,84,94,95)
and m._Organism_key = s._Organism_key
and r._Object_key_2 = m._Marker_key
and r._Category_key in (1004,1006)
and r._Object_key_1 = a._Allele_key
and r._RelationshipTerm_key = t._Term_key
and m._Marker_key = eg._Object_key
and eg._MGIType_key = 2
and eg._LogicalDB_key = 55
and a._Allele_key = aa._Object_key
and aa._MGIType_key = 11
and not exists (select 1 from DP_EntrezGene_Info e, ACC_Accession a
        where m._Marker_key = a._Object_key
        and a._MGIType_key = 2
        and a.accID = e.geneID)
-- not recombinase
and not exists (select 1 from VOC_Annot va
        where va._AnnotType_key = 1014
        and r._Object_key_1 = va._Object_key
        and va._Term_key = 11025588
        )

union
select m._Marker_key, m._Organism_key, s.commonname, m.symbol as msymbol, a.symbol as asymbol, t.term as relationshipTerm, 
'none', aa.accid as alleleID
from MRK_Marker m, MGI_Organism s, MGI_Relationship r, ALL_Allele a, VOC_Term t, ACC_Accession aa
where m._Organism_key in (2,10,11,13,40,63,84,94,95)
and m._Organism_key = s._Organism_key
and r._Object_key_2 = m._Marker_key
and r._Category_key in (1004,1006)
and r._Object_key_1 = a._Allele_key
and r._RelationshipTerm_key = t._Term_key
and a._Allele_key = aa._Object_key
and aa._MGIType_key = 11
and not exists (select 1 from DP_EntrezGene_Info e
        where m.symbol = e.symbol
        )
-- not recombinase
and not exists (select 1 from VOC_Annot va
        where va._AnnotType_key = 1014
        and r._Object_key_1 = va._Object_key
        and va._Term_key = 11025588
        )

)
order by commonname, msymbol, egID
''', 'auto')

for r in results:
    fp.write(r['egID'] + TAB)
    fp.write(r['msymbol'] + TAB)
    fp.write(r['commonname'] + TAB)
    fp.write(r['relationshipTerm'] + TAB)
    fp.write(r['alleleID'] + TAB)
    fp.write(r['asymbol'] + CRT)

fp.write(CRT)
fp.write('\n(%d rows affected)\n\n' % (len(results)))

db.useOneConnection(0)
reportlib.finish_nonps(fp)	# non-postscript file
