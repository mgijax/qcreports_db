
'''
#
# TR12672/Lit Triage
#
# Report:
#
#	The reference must be:
#	group = GO, status = 'Full-coded'
# 	No GO Annotation (_AnnotType_key = 1000)
#	output:
#	1. J#
#	2. Creation Date
#	4. extracted text (80 characters/around text)
#
# Usage:
#       WF_GO_FullCodeNoAnnot.py
#
# Notes:
#
# History:
#
# 09/29/2017
#	- TR12250/Lit Triage
#
'''
 
import sys 
import os 
import re
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

fp = reportlib.init(sys.argv[0], 'References with GO status "Full-coded" where there is no GO annotation', os.environ['QCOUTPUTDIR'])

fp.write('''
        The reference must be:
             group = GO, status = 'Full-coded'
             No GO annotation
''')

results = db.sql('''select distinct a.accid as jnumID, b.isDiscard, 
        to_char(b.creation_date, 'MM/dd/yyyy') as cdate
    from BIB_Workflow_status wf, ACC_Accession a, BIB_Refs b
    where wf._Group_key = 31576666
    and wf.isCurrent = 1
    and wf._Status_key = 31576674
    and wf._Refs_key = a._Object_key
    and a._MGIType_key = 1
    and a._LogicalDB_key = 1
    and a.prefixPart = 'J:'
    and a.preferred = 1
    and wf._Refs_key = b._Refs_key
    and not exists (select 1
    from VOC_Annot a, VOC_Evidence e
    where a._AnnotType_key = 1000
    and a._Annot_key = e._Annot_key
    and e._Refs_key = wf._Refs_key)
    order by a.accid''', 'auto')
fp.write('JNumber%sisDiscard%sCreation Date%s' % (TAB, TAB, CRT))
fp.write('-' * 40 + CRT)
for r in results:
        jnumID = r['jnumID']
        isDiscard = r['isDiscard']
        cdate = r['cdate']
        fp.write('%s%s%d%s%s%s' % (jnumID, TAB, isDiscard, TAB, cdate, CRT))
fp.write('\nTotal: %d\n' % len(results))

reportlib.finish_nonps(fp)
