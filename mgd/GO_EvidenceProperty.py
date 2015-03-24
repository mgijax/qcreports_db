#!/usr/local/bin/python

'''
#
# GO_EvidenceProperty.py
#
# Report:
#       
# A report that inspects J:73065 GO annotations and 
# emails GO curators (Mgi-go@jax.org) if the external ref properties 
# field is not filled (should have a PMID followed by pipe and an evidence code
# or has a bad format - The expected format is PMID:XXXXX|YYYY
# where YYYY is the evidence code
#
#
# field 1: Gene Accession ID 
# field 2: Gene Symbol
# field 3: GO ID 
# field 4: user 
#
# Usage:
#      GO_EvidenceProperty.py 
#
# History:
#
# 03/10/2014	lnh
#	- TR 11332
#
'''
 
import sys 
import os
import string
import reportlib
from datetime import datetime

#
#Set up email contact
#
sender = "mgiadmin@lindon.informatics.jax.org"
receiver = "Mgi-go@jax.org"
#receiver = "lnh@jax.org"

try:
    if os.environ['DB_TYPE'] == 'postgres':
        import pg_db
        db = pg_db
        db.setTrace()
        db.setAutoTranslateBE()
    else:
        import db
except:
    import db


CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

def printNoExtResults(cmd):
    results = db.sql(cmd, 'auto')
    fp.write('total number without external ref value: %s\n' % (len(results)))
    fp.write('MGI-ID' + TAB)
    fp.write('Gene Symbol' + TAB)
    fp.write('GO-ID' + TAB)
    fp.write('User' + 2*CRT)
    missCount=0
    for r in results:
        fp.write(r['accID'] + TAB)
        fp.write(r['symbol'] + TAB)
        fp.write(r['goaccID'] + TAB)
        fp.write(r['dbuser'] + CRT)
        missCount+=1
    return missCount

def printBadExtResults(cmd):
    results = db.sql(cmd, 'auto')
    fp.write('\nTotal number with missing PMID in external ref value: %s\n\n' % (len(results)))
    fp.write('MGI-ID' + TAB)
    fp.write('Gene Symbol' + TAB)
    fp.write('GO-ID' + TAB)
    fp.write('EvidencePropertyValue' + TAB)
    fp.write('User' + 2*CRT)
    badCount=0
    for r in results:
        fp.write(r['accID'] + TAB)
        fp.write(r['symbol'] + TAB)
        fp.write(r['goaccID'] + TAB)
        fp.write(r['pValue'] + TAB)
        fp.write(r['dbuser'] + CRT)
        badCount+=1
    return badCount

def printMissEvCodeResults(cmd,evidenceMap):
    results = db.sql(cmd, 'auto')
    fp.write('\nCases with missing evidence code in external ref value: \n\n' + TAB)
    fp.write('MGI-ID' + TAB)
    fp.write('Gene Symbol' + TAB)
    fp.write('GO-ID' + TAB)
    fp.write('EvidencePropertyValue' + TAB)
    fp.write('User' + 2*CRT)
    badCount=0
    for r in results:
        fields=r['pValue'].split('|')
        if len(fields)>1:
           ecode=fields[1].strip()
           if ecode not in evidenceMap:
              fp.write(r['accID'] + TAB)
              fp.write(r['symbol'] + TAB)
              fp.write(r['goaccID'] + TAB)
              fp.write(r['pValue'] + TAB)
              fp.write(r['dbuser'] + CRT)
              badCount+=1
        else:
              fp.write(r['accID'] + TAB)
              fp.write(r['symbol'] + TAB)
              fp.write(r['goaccID'] + TAB)
              fp.write(r['pValue'] + TAB)
              fp.write(r['dbuser'] + CRT)
              badCount+=1

    return badCount

#
# Main
#
#Note: Harold said for now the generated report should be stored under the tr directory
#     When he changes his mind, we will set outputdir=os.environ['QCOUTPUTDIR']
#

fp = reportlib.init(sys.argv[0], fileExt = '.rpt', outputdir = '/mgi/all/wts_projects/11300/11332/', printHeading = None)
i = datetime.now()
fp.write("Date:"+i.strftime('%Y/%m/%d %I:%M:%S \n\n'))

#
# Get all GO/Marker evidence annotations records for J:73065 -> _refs_key=74017
# _annottyp_key=1000 (GO/Marker); exclude annotations where _user_key=1503 (login=GOC)
#
db.sql('''
        select ve._annotevidence_key,va._term_key,va._object_key,m.login
        into #goevidence
        from  voc_evidence ve,voc_annot va, mgi_user m
        where ve._refs_key=74017
        and   ve._createdby_key= m._user_key
        and   m._user_key!=1503
        and   ve._annot_key=va._annot_key
        and   va._annottype_key=1000
        ''', None)
db.sql('create index goevidence_idx1 on #goevidence(_object_key)', None)

#
# Add marker symbol and marker accession id
#
db.sql('''
        select distinct va._term_key,va._annotevidence_key,va.login,m.symbol,ac.accID as mgiID 
        into #gomarkers
        from #goevidence va , mrk_marker m,acc_accession ac
        where va._object_key=m._marker_key
        and va._object_key=ac._object_key
        and ac._mgitype_key=2  
        and ac._logicaldb_key=1
        and ac.preferred=1 
	''', None)
db.sql('create index gormarkers_idx1 on #gomarkers(_term_key)', None)

#
# Add GO IDS to the list
#
db.sql('''
        select gm._annotevidence_key,gm.login,gm.symbol,gm.mgiID,ac.accID as GOID
        into #gomarkersIDs
        from #gomarkers gm,acc_accession ac
        where gm._term_key=ac._object_key
        and ac._mgitype_key=13 and  ac._logicaldb_key=31
        and ac.preferred = 1 
        ''', None)
db.sql('create index gormarkersIDs_idx1 on #gomarkersIDs(_annotevidence_key)', None)

#
#Get all evidences records with evidence property term="external ref" _propertyterm_key=6481778
#
db.sql('''
        select _annotevidence_key,value
        into #evidenceproperty
        from voc_evidence_property
        where _propertyterm_key=6481778
        ''', None)
db.sql('create index evidenceproperty_idx1 on #evidenceproperty(_annotevidence_key)', None)

#
#Get GO evidence codes
#
db.sql('''
        select abbreviation
        into #goevidencecode
        from voc_term
        where _vocab_key=3
        ''', None)

cmd ="  select mgiID as accID,symbol,GOID as goaccID,login as dbuser from #gomarkersIDs "
cmd +=" where _annotevidence_key not in (select _annotevidence_key from #evidenceproperty)"

missCount=printNoExtResults(cmd)

cmd ="  select mgiID as accID,symbol,GOID as goaccID,login as dbuser,value as pValue "
cmd+="from #gomarkersIDs g, #evidenceproperty e WHERE  g._annotevidence_key=e._annotevidence_key"
cmd +=" and value not like 'PMID:%'"

badCount=printBadExtResults(cmd)

#
# get the list of current go evidence code
#
evidenceMap={}
cmd=" select abbreviation from #goevidencecode "
results = db.sql(cmd, 'auto')

for r in results:
    evidenceMap[r['abbreviation'].strip()]=1

#get all evidence that begins with PMID but are missing the evidence code
cmd ="  select mgiID as accID,symbol,GOID as goaccID,login as dbuser,value as pValue "
cmd+="from #gomarkersIDs g, #evidenceproperty e WHERE  g._annotevidence_key=e._annotevidence_key"
cmd +=" and value like 'PMID:%'"
badCount += printMissEvCodeResults(cmd,evidenceMap)

# Create message container - the correct MIME type is multipart/alternative.
message = """
  You have made one or more annotations using J:73065 and have not filled in the external 
  reference properties box. Or the external reference properties box was not filled properly(should have a PMID followed by pipe and an evidence code).
 Please correct this information today -(http://prodwww.informatics.jax.org/all/wts_projects/11300/11332/)

 Note: This report runs daily
"""
cmd="echo \""+message+"\" | mailx -r \""+sender+"\" -s \"J:73065 GO Annotations Alert - External Ref\" \""+receiver+"\""
mes="Missing External Ref total: %s  Bad format Total: %s" % (missCount,badCount)

print mes
if missCount>0 or badCount>0:
   try:
       os.system(cmd)
       print "Successfully sent email"
   except  OSError,e:
       print "Error: unable to send email"

print "\nProgram Complete\n"
reportlib.finish_nonps(fp)

