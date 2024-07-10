
'''
#
# PubMed Id in/not in MGI
#
# Enter PubMed Id. 
# If PubMed Id exists in MGI, then display PubMed Id and isDiscard value.
#
'''
 
import sys
import os
import db
import reportlib

#db.setTrace()

CRT = reportlib.CRT
TAB = reportlib.TAB

def go (form) :
    arg = form['arg'].value
    # expects "1111 2222 3333"
    value = list(arg.split(' '))

    # example: '1111','2222','3333'
    value1 = "'" + "','".join(value) + "'"

    # example: ('1111'),('2222'),('3333')
    value2 = ""
    for v in value:
            value2 = value2 + "('" + v + "'),"
    value2 = value2[:-1]

    results = db.sql('''
    select pubmedID, jnumID, relevanceterm 
    from bib_citation_cache 
    where pubmedid in (%s) 
    union 
    select list, null, null 
    from (values %s) s(list) 
    where not exists (select 1 from bib_citation_cache c where s.list = c.pubmedid) 
    order by relevanceterm
    ''' % (value1, value2), 'auto')

    sys.stdout.write('pubmedID' + TAB)
    sys.stdout.write('jnumID' + TAB)
    sys.stdout.write('relevanceterm' + CRT)

    for r in results:
            sys.stdout.write(r['pubmedID'] + TAB)

            if r['jnumID'] == None:
                    sys.stdout.write(TAB)
            else:
                    sys.stdout.write(r['jnumID'] + TAB)

            if r['relevanceterm'] == None:
                    sys.stdout.write(CRT)
            else:
                    sys.stdout.write(r['relevanceterm'] + CRT)

    sys.stdout.flush()

