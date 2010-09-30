#!/usr/local/bin/python

'''
#
# GO_stats.py
#
# Report:
#       
# 09/30/2010	lec
#	- moved goStats.sh to python
#
# 09/01/2010    lec
#       - TR 9962/TR10341
#       "HAND" renamed "Total Non-IEA"
#
# 08/18/2010    lec
#       - TR 10318/add GOC Annotations, Curator Annotations
#       - Curator Annotations: CURATOR_CLAUSE
#                              EVIDENCE_CLAUSE
#                              created by not in GOC_CLAUSE
#
# 02/23/2010    lec
#       - TR 10035/add J:155856 to orthology section
#       - change EQUALS "=" to "in"
#
# 10/20/2009    lec
#       - TR 9894/add a GOA annotation check: setCreatedByClause, GOA_CLAUSE
#       this report can/should probably be moved to a python report
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

#ROOT="J:73796"
ROOT_CLAUSE="(74750)"

#ORTHOLOGY="J:73065,J:155856"/74017/156949
ORTHOLOGY_CLAUSE="(74017,156949)"

#SWISS_PROT="J:60000"
SWISSPROT_CLAUSE="(61933)"

#INTERPRO="J:72247"
INTERPRO_CLAUSE="(73199)"

#EC="J:72245"
EC_CLAUSE="(73197)"

#SWISS_PROT, INTERPRO, EC
IEA_CLAUSE="(61933,73199,73197)"

#RGD="J:155856"/156949
#SWISS_PROT, INTERPRO, EC, RGD
CURATOR_CLAUSE="(61933,73199,73197,156949)"

# 115 = IEA
# 118 = ND
EVIDENCE_CLAUSE="(115,118)"

# MGI_User.login names
GOA_CLAUSE="'GOA_%'"
GOC_CLAUSE="'GOC'"
REFGENOME_CLAUSE="'RefGenome'"
GO_CLAUSE="('GOC', 'RefGenome') "

byReference = 'and e._Refs_key %s'
byCreatedBy = 'and u.login %s'
byEvidenceCode = 'and e._EvidenceTerm_key %s'

#
# count by gene
#
byGene1 = '''
select count(distinct a._Object_key)
from VOC_Annot a, VOC_Evidence e, MGI_User u
where a._AnnotType_key  = 1000
and a._Annot_key = e._Annot_key
and e._CreatedBy_key = u._User_Key
%s
%s
%s
'''

#
# count by gene, grouped by dag name
#
byGene2 = '''
select d.name, terms = convert (char(6), count(distinct a._Object_key))
from VOC_Annot a, VOC_Evidence e, DAG_Node n, DAG_DAG d, MGI_User u
where a._AnnotType_key = 1000
and a._Term_key = n._Object_key
and d._DAG_Key = n._DAG_Key
and a._Annot_key = e._Annot_key
and e._CreatedBy_key = u._User_Key
%s
%s
%s
group by d.name
'''

#
# count by annotation
#
byAnnot1 = '''
select count(a._Annot_key)
from VOC_Annot a, VOC_Evidence e, MGI_User u
where a._AnnotType_key  = 1000
and a._Annot_key = e._Annot_key
and e._CreatedBy_key = u._User_Key
%s
%s
%s
'''

#
# count by annotation, group by dag name
#
byAnnot2 = '''
select d.name, terms = convert (char(6), count(a._Annot_key))
from VOC_Annot a, VOC_Evidence e, DAG_Node n, DAG_DAG d, MGI_User u
where a._AnnotType_key = 1000
and a._Term_key = n._Object_key
and d._DAG_Key = n._DAG_Key
and a._Annot_key = e._Annot_key
and e._CreatedBy_key = u._User_Key
%s
%s
%s
group by d.name
'''

#
# summary 1
# number of GO Terms per Ontology
#
def goSummary1():

    fp.write('*********************************************************************\n')
    fp.write('GO Ontology Summary - Number of GO Terms per Ontology\n\n')
    fp.write(string.ljust('ontology', 25) + TAB)
    fp.write(string.ljust('number of terms', 25) + CRT)
    fp.write(string.ljust('--------', 25) + TAB)
    fp.write(string.ljust('---------------', 25) + CRT)

    results = db.sql('''
           select name = substring(d.name,1,30), terms = count(n._Object_key)
           from DAG_DAG d, DAG_Node n
           where d._DAG_key in (1,2,3)
           and d._DAG_key = n._DAG_key
           group by d._DAG_key
	   ''', 'auto')

    for r in results:
	fp.write(string.ljust(r['name'], 25) + TAB)
	fp.write(string.ljust(`r['terms']`, 25) + CRT)

    fp.write('\n*********************************************************************\n')

#
# summary 2
# number of GO Terms per Ontology used in MGI
#
def goSummary2():

    fp.write('*********************************************************************\n')
    fp.write('GO Ontology Summary - Number of GO Terms per Ontology Used in MGI\n\n')
    fp.write(string.ljust('ontology', 25) + TAB)
    fp.write(string.ljust('number of terms', 25) + CRT)
    fp.write(string.ljust('--------', 25) + TAB)
    fp.write(string.ljust('---------------', 25) + CRT)

    results = db.sql('''
	   select name = substring(d.name,1,30), terms = count(n._Object_key)
	   from DAG_DAG d, DAG_Node n
	   where d._DAG_key in (1,2,3)
	   and d._DAG_key = n._DAG_key
	   and exists (select 1 from VOC_Annot a where n._Object_key = a._Term_key)
	   group by d._DAG_key
	   ''', 'auto')

    for r in results:
	fp.write(string.ljust(r['name'], 25) + TAB)
	fp.write(string.ljust(`r['terms']`, 35) + CRT)

    fp.write('\n*********************************************************************\n')

#
# specific annotation counts by annotation "name"
#
def writeCount(name):

   fp.write('*********************************************************************\n')
   fp.write('%s Annotations:\n' % (name))
   fp.write('======================\n')

   if name == "ALL":
	# all annotations

       results1 = db.sql(byGene1 % ('', '', ''), 'auto')
       results2 = db.sql(byGene2 % ('', '', ''), 'auto')
       results3 = db.sql(byAnnot1 % ('', '', ''), 'auto')
       results4 = db.sql(byAnnot2 % ('', '', ''), 'auto')

   elif name == "Total Non-IEA":
	# not in IEA references

       results1 = db.sql(byGene1 % (byReference % ('not in ' + IEA_CLAUSE), '', ''), 'auto')
       results2 = db.sql(byGene2 % (byReference % ('not in ' + IEA_CLAUSE), '', ''), 'auto')
       results3 = db.sql(byAnnot1 % (byReference % ('not in ' + IEA_CLAUSE), '', ''), 'auto')
       results4 = db.sql(byAnnot2 % (byReference % ('not in ' + IEA_CLAUSE), '', ''), 'auto')

   elif name == "Total IEA":
	# in IEA references

       results1 = db.sql(byGene1 % (byReference % ('in ' + IEA_CLAUSE), '', ''), 'auto')
       results2 = db.sql(byGene2 % (byReference % ('in ' + IEA_CLAUSE), '', ''), 'auto')
       results3 = db.sql(byAnnot1 % (byReference % ('in ' + IEA_CLAUSE), '', ''), 'auto')
       results4 = db.sql(byAnnot2 % (byReference % ('in ' + IEA_CLAUSE), '', ''), 'auto')

   elif name == "Curator":
	# not in IEA references
	# not like "GOA"
	# not in rest of GO GAFs
	# not in evidence codes (see above)

       results1 = db.sql(byGene1 % (byReference % ('not in ' + CURATOR_CLAUSE), \
			byCreatedBy % ('not in ' + GO_CLAUSE) + \
			byCreatedBy % ('not like ' + GOA_CLAUSE), \
			byEvidenceCode % ('not in ' + EVIDENCE_CLAUSE)), 'auto')
       results2 = db.sql(byGene2 % (byReference % ('not in ' + CURATOR_CLAUSE), \
			byCreatedBy % ('not in ' + GO_CLAUSE) + \
			byCreatedBy % ('not like ' + GOA_CLAUSE), \
			byEvidenceCode % ('not in ' + EVIDENCE_CLAUSE)), 'auto')
       results3 = db.sql(byAnnot1 % (byReference % ('not in ' + CURATOR_CLAUSE), \
			byCreatedBy % ('not in ' + GO_CLAUSE) + \
			byCreatedBy % ('not like ' + GOA_CLAUSE), \
			byEvidenceCode % ('not in ' + EVIDENCE_CLAUSE)), 'auto')
       results4 = db.sql(byAnnot2 % (byReference % ('not in ' + CURATOR_CLAUSE), \
			byCreatedBy % ('not in ' + GO_CLAUSE) + \
			byCreatedBy % ('not like ' + GOA_CLAUSE), \
			byEvidenceCode % ('not in ' + EVIDENCE_CLAUSE)), 'auto')

   elif name == "GOA":
	# not in IEA references
	# in "GOA_%" user

       results1 = db.sql(byGene1 % (byReference % ('not in ' + IEA_CLAUSE), \
			byCreatedBy % ('like ' + GOA_CLAUSE), \
			''), 'auto')
       results2 = db.sql(byGene2 % (byReference % ('not in ' + IEA_CLAUSE), \
			byCreatedBy % ('like ' + GOA_CLAUSE), \
			''), 'auto')
       results3 = db.sql(byAnnot1 % (byReference % ('not in ' + IEA_CLAUSE), \
			byCreatedBy % ('like ' + GOA_CLAUSE), \
			''), 'auto')
       results4 = db.sql(byAnnot2 % (byReference % ('not in ' + IEA_CLAUSE), \
			byCreatedBy % ('like ' + GOA_CLAUSE), \
			''), 'auto')

   elif name == "GOC":
	# not in IEA references
	# in "GOC" user

       results1 = db.sql(byGene1 % (byReference % ('not in ' + IEA_CLAUSE), \
			byCreatedBy % ('= ' + GOC_CLAUSE), \
			''), 'auto')
       results2 = db.sql(byGene2 % (byReference % ('not in ' + IEA_CLAUSE), \
			byCreatedBy % ('= ' + GOC_CLAUSE), \
			''), 'auto')
       results3 = db.sql(byAnnot1 % (byReference % ('not in ' + IEA_CLAUSE), \
			byCreatedBy % ('= ' + GOC_CLAUSE), \
			''), 'auto')
       results4 = db.sql(byAnnot2 % (byReference % ('not in ' + IEA_CLAUSE), \
			byCreatedBy % ('= ' + GOC_CLAUSE), \
			''), 'auto')

   elif name == "RefGenome":
	# not in IEA references
	# in "RefGenome" user

       results1 = db.sql(byGene1 % (byReference % ('not in ' + IEA_CLAUSE), \
			byCreatedBy % ('= ' + REFGENOME_CLAUSE), \
			''), 'auto')
       results2 = db.sql(byGene2 % (byReference % ('not in ' + IEA_CLAUSE), \
			byCreatedBy % ('= ' + REFGENOME_CLAUSE), \
			''), 'auto')
       results3 = db.sql(byAnnot1 % (byReference % ('not in ' + IEA_CLAUSE), \
			byCreatedBy % ('= ' + REFGENOME_CLAUSE), \
			''), 'auto')
       results4 = db.sql(byAnnot2 % (byReference % ('not in ' + IEA_CLAUSE), \
			byCreatedBy % ('= ' + REFGENOME_CLAUSE), \
			''), 'auto')

   elif name == "ORTHOLOGY":
	# in orthology reference

       results1 = db.sql(byGene1 % (byReference % ('in ' + ORTHOLOGY_CLAUSE), '', ''), 'auto')
       results2 = db.sql(byGene2 % (byReference % ('in ' + ORTHOLOGY_CLAUSE), '', ''), 'auto')
       results3 = db.sql(byAnnot1 % (byReference % ('in ' + ORTHOLOGY_CLAUSE), '', ''), 'auto')
       results4 = db.sql(byAnnot2 % (byReference % ('in ' + ORTHOLOGY_CLAUSE), '', ''), 'auto')

   elif name == "SWISS_PROT":
	# in SWISS_PROT reference

       results1 = db.sql(byGene1 % (byReference % ('in ' + SWISSPROT_CLAUSE), '', ''), 'auto')
       results2 = db.sql(byGene2 % (byReference % ('in ' + SWISSPROT_CLAUSE), '', ''), 'auto')
       results3 = db.sql(byAnnot1 % (byReference % ('in ' + SWISSPROT_CLAUSE), '', ''), 'auto')
       results4 = db.sql(byAnnot2 % (byReference % ('in ' + SWISSPROT_CLAUSE), '', ''), 'auto')

   elif name == "INTERPRO":
	# in INTERPRO reference

       results1 = db.sql(byGene1 % (byReference % ('in ' + INTERPRO_CLAUSE), '', ''), 'auto')
       results2 = db.sql(byGene2 % (byReference % ('in ' + INTERPRO_CLAUSE), '', ''), 'auto')
       results3 = db.sql(byAnnot1 % (byReference % ('in ' + INTERPRO_CLAUSE), '', ''), 'auto')
       results4 = db.sql(byAnnot2 % (byReference % ('in ' + INTERPRO_CLAUSE), '', ''), 'auto')

   elif name == "EC":
	# in EC reference

       results1 = db.sql(byGene1 % (byReference % ('in ' + EC_CLAUSE), '', ''), 'auto')
       results2 = db.sql(byGene2 % (byReference % ('in ' + EC_CLAUSE), '', ''), 'auto')
       results3 = db.sql(byAnnot1 % (byReference % ('in ' + EC_CLAUSE), '', ''), 'auto')
       results4 = db.sql(byAnnot2 % (byReference % ('in ' + EC_CLAUSE), '', ''), 'auto')

   elif name == "ROOT":
	# in ROOT reference

       results1 = db.sql(byGene1 % (byReference % ('in ' + ROOT_CLAUSE), '', ''), 'auto')
       results2 = db.sql(byGene2 % (byReference % ('in ' + ROOT_CLAUSE), '', ''), 'auto')
       results3 = db.sql(byAnnot1 % (byReference % ('in ' + ROOT_CLAUSE), '', ''), 'auto')
       results4 = db.sql(byAnnot2 % (byReference % ('in ' + ROOT_CLAUSE), '', ''), 'auto')

   # total by gene
   fp.write('Total Number of Genes Annotated to:' + TAB + str(results1[0]['']) + '\n')

   # breakdown by ontology/dag
   fp.write('Breakdown by OntologyName:\n')

   for r in results2:
	fp.write(string.ljust(r['name'], 25) + TAB)
	fp.write(string.ljust(r['terms'], 45) + CRT)

   fp.write('---------------------------------------------------------------------\n')

   # total by annotation
   fp.write('Total Number of Annotations:' + TAB + str(results3[0]['']) + '\n')

   # breakdown by ontology/dag
   fp.write('Breakdown by OntologyName:\n')

   for r in results4:
	fp.write(string.ljust(r['name'], 25) + TAB)
	fp.write(string.ljust(r['terms'], 45) + CRT)

   fp.write('*********************************************************************\n')

#
# Main
#

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'])

goSummary1()
goSummary2()
writeCount('ALL')
writeCount('Total Non-IEA')
writeCount('GOC')
writeCount('Curator')
writeCount('GOA')
writeCount('ORTHOLOGY')
writeCount('RefGenome')
writeCount('Total IEA')
writeCount('SWISS_PROT')
writeCount('INTERPRO')
writeCount('EC')
writeCount('ROOT')

reportlib.finish_nonps(fp)

