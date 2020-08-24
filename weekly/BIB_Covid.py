#
# Report:
#       Coronaviruas related references
#
#       refenreces where bib_workflow_tab contains 'cov:%'
#
# History:
#
# lec	08/24/2020
#	- TR13369/QC report of COV: tagged papers : Sue Bellow (smb)
#
 
import sys 
import os
import db
import reportlib

db.setTrace()

fp = reportlib.init(sys.argv[0], 'Coronaviruas related references', outputdir = os.environ['QCOUTPUTDIR'],  printHeading = None)

fp.write('*1.  workflow tags\n')
fp.write('*2.  authors\n')
fp.write('*3.  title\n')
fp.write('*4.  abstract\n')
fp.write('*5.  year\n')
fp.write('*6.  journal\n')
fp.write('*7.  PMID\n')
fp.write('*8.  J#\n')
fp.write('*9.  markers\n')
fp.write('*10. alleles\n')
fp.write('*11. strains\n')
fp.write('*12. DOID-allele\n')
fp.write('*13. DOID-genotype\n')
fp.write('\n')

#
# refenreces where bib_workflow_tab contains 'cov:%'
#
db.sql('''
select distinct covid._refs_key
into temp table covid
from bib_workflow_tag covid, voc_term t
where covid._tag_key = t._term_key
and t._vocab_key = 129
and t.term ilike 'cov:%'
''', None)
db.sql('create index idx_refs on covid(_Refs_key)', None)

#
# markers associated with covid reference
#
cmd = '''
select covid._refs_key, m.symbol
from covid, mgi_reference_marker_view m
where covid._refs_key = m._refs_key
'''

results = db.sql(cmd, 'auto')
markers = {}
for r in results:
    key = r['_refs_key']
    value = r['symbol']
    if key not in markers:
        markers[key] = []
    markers[key].append(value)
#print(markers)

#
# alleles associated with covid reference
#
cmd = '''
select covid._refs_key, m.symbol
from covid, mgi_reference_allele_view m
where covid._refs_key = m._refs_key
'''

results = db.sql(cmd, 'auto')
alleles = {}
for r in results:
    key = r['_refs_key']
    value = r['symbol']
    if key not in alleles:
        alleles[key] = []
    alleles[key].append(value)
#print(alleles)

#
# strains associated with covid reference
#
cmd = '''
select covid._refs_key, m.strain
from covid, mgi_reference_strain_view m
where covid._refs_key = m._refs_key
'''

results = db.sql(cmd, 'auto')
strains = {}
for r in results:
    key = r['_refs_key']
    value = r['strain']
    if key not in strains:
        strains[key] = []
    strains[key].append(value)
#print(strains)

#
# do/allele annotations associated with covid reference
#
cmd = '''
select distinct covid._refs_key, a.accID
from covid, voc_evidence e, voc_annot v, acc_accession a
where covid._refs_key = e._refs_key
and e._annot_key = v._annot_key
and v._annottype_key = 1021
and v._term_key = a._object_key
and a._logicaldb_key = 191
'''

results = db.sql(cmd, 'auto')
doiallele = {}
for r in results:
    key = r['_refs_key']
    value = r['accID']
    if key not in doiallele:
        doiallele[key] = []
    doiallele[key].append(value)
#print(doiallele)

#
# do/genotype annotations associated with covid reference
#
cmd = '''
select distinct covid._refs_key, a.accID
from covid, voc_evidence e, voc_annot v, acc_accession a
where covid._refs_key = e._refs_key
and e._annot_key = v._annot_key
and v._annottype_key = 1020
and v._term_key = a._object_key
and a._logicaldb_key = 191
'''

results = db.sql(cmd, 'auto')
doigenotype = {}
for r in results:
    key = r['_refs_key']
    value = r['accID']
    if key not in doigenotype:
        doigenotype[key] = []
    doigenotype[key].append(value)
#print(doigenotype)

#
# workflow tags
#
cmd = '''
select covid._refs_key, t.term
from covid, bib_workflow_tag tg, voc_term t
where covid._refs_key = tg._refs_key
and tg._tag_key = t._term_key
order by covid._refs_key
'''

results = db.sql(cmd, 'auto')
tags = {}
for r in results:
    key = r['_refs_key']
    value = r['term']
    if key not in tags:
        tags[key] = []
    tags[key].append(value)
#print(tags)

#
# reference info
#
cmd = '''select distinct covid._refs_key, b.jnumid, b.pubmedid, r.authors, r.title, r.year, r.journal, r.abstract
from bib_workflow_tag covid, voc_term t, bib_citation_cache b, bib_refs r
where covid._tag_key = t._term_key
and t._vocab_key = 129
and t.term ilike 'cov:%'
and covid._refs_key = b._refs_key
and covid._refs_key = r._refs_key
order by journal
'''

results = db.sql(cmd, 'auto')

for r in results:
    key = r['_refs_key']

    if key in tags:
        fp.write('|'.join(tags[key]))
    fp.write('\t')

    fp.write(r['authors'] + '\t')
    fp.write(r['title'] + '\t')

    if r['abstract'] != None:
        fp.write(r['abstract'])
    fp.write('\t')

    fp.write(str(r['year']) + '\t')
    fp.write(r['journal'] + '\t')

    if r['pubmedid'] != None:
        fp.write(r['pubmedid'])
    fp.write('\t')

    if r['jnumid'] != None:
        fp.write(r['jnumid'])
    fp.write('\t')

    if key in markers:
        fp.write('|'.join(markers[key]))
    fp.write('\t')

    if key in alleles:
        fp.write('|'.join(alleles[key]))
    fp.write('\t')

    if key in strains:
        fp.write('|'.join(strains[key]))
    fp.write('\t')
        
    if key in doiallele:
        fp.write('|'.join(doiallele[key]))
    fp.write('\t')
        
    if key in doigenotype:
        fp.write('|'.join(doigenotype[key]))
    fp.write('\n')
        
reportlib.finish_nonps(fp)

