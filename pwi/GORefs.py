
'''
#
# Purpose:
#
#	Generate an HTML report of Potential GO References
#	for the given Gene.  Highlight all GO Terms which
#	are embedded in either the Title or Abstract of each
#	Reference.  Order the References by the number of matches
#	(descending).
#
# Inputs:
#	SQL command which selects an _Object_key and description of the Gene
#
# This is called from the pwi/api/GO annotation module:  see mgd_java_api/app.properties
#
# add to:  qcreports_db/pwi
# add to:  mgd_java_api/app.properties.default
# remove from : pgdbutilities/bin/ei/
#
'''

import sys
import os
import db
import reportlib
import mgi_utils

# HTML constants

PROD_URL = '''
<A HREF="http://prodwww.informatics.jax.org/pwi/summary/reference?accids=%s">%s</A>
        '''

TITLE ='<HEAD><TITLE>'
EOTITLE = '</TITLE></HEAD>'
LB = '<BR>'
PB = '<P>'
HR = '<HR>'
PRE = '<PRE>'
EOP = '</PRE>'
H = '<H1>'
EOH = '</H1>'
BOLD = '<B>'
EOB = '</B>'

CRT = reportlib.CRT

def scanText(text):
        '''
        #
        # parameters:  text (str., the text to scan
        #
        # assumes: global terms{} has been initialized
        #
        # effects:
        # 	replaces all instances of GO terms in "text" with HTML bold markup
        #	for example:  "receptor" ==> "<B>receptor</B>"
        #
        # returns: number of terms matched and the marked-up text
        #
        '''

        numTerms = 0
        text1 = text
        text2 = ''

        if text1 != None:
                for i in range(len(terms)):
                        term = terms[i]
                        if text1.find(term) >= 0:
                                highlighted = '<B>%s</B>' % term
                                text2 = text1.replace(term, highlighted)
                                text1 = text2
                                numTerms = numTerms + 1

        return numTerms, text1

#
# Main
#

# expects _Object_key and description fields
userlogin = sys.argv[2].replace('\n', '')
cmd = 'select distinct _Object_key, description from MRK_Summary_View where _Object_key = ' + userlogin
results = db.sql(cmd, 'auto')

markerKey = results[0]['_Object_key']
# description is expected in the format "symbol, name...."
description = results[0]['description']
tokens = description.split(', ')
symbol = tokens[0]

# initialize report output file
userhome = '/home/' + sys.argv[1] + '/mgireport'
#fp = reportlib.init('GO%s' % (symbol), printHeading = None, isHTML = 1, outputdir = os.environ['EIREPORTDIR'], sqlOneConnection = 0, sqlLogging = 0)
fp = reportlib.init('GO%s' % (symbol), printHeading = None, isHTML = 1, outputdir = userhome, sqlOneConnection = 0, sqlLogging = 0)
fp.write(EOP)
fp.write(TITLE + 'Potential New GO References' + EOTITLE + CRT)
fp.write(H + 'Potential New GO References' + EOH + CRT)
fp.write(H + 'Symbol: %s' % (description) + EOH + CRT)
fp.write('Start Date/Time:  %s' % (mgi_utils.date()) + CRT + LB + HR)

# read terms & synonyms into dictionary
terms = []
cmd = '''
        select distinct term 
        from VOC_Term 
        where _Vocab_key = 4 
        and term not like '%(sensu %' and term != 'cell' 
        '''
results = db.sql(cmd, 'auto')
for r in results:
        terms.append(r['term'])

cmd = '''
      select distinct s.synonym 
      from VOC_Term v, MGI_Synonym s 
      where v._Vocab_key = 4 
      and v._Term_key = s._Object_key 
      and s._MGIType_key = 13
      '''
results = db.sql(cmd, 'auto')
for r in results:
        terms.append(r['synonym'])

# select no-go references for given marker key
cmd = '''
      select r.jnumID, r.title, r.short_citation, rr.abstract 
      from BIB_GOXRef_View r, BIB_Refs rr
      where r._Marker_key = %d
      and not exists (select 1 from VOC_Annot a, VOC_Evidence e 
      where a._AnnotType_key = 1000 
      and a._Annot_key = e._Annot_key 
      and e._Refs_key = r._Refs_key) 
      and r._Refs_key = rr._Refs_key
      order by r.jnum desc
      ''' % (markerKey)
results = db.sql(cmd, 'auto')

ref = {}		# {'J:, Citation + Abstract' : number of GO Terms matched}
recs = 0		# record counter

# for each reference, scan the title and abstract for GO Terms.
# the title/abstract text which matches GO Terms will be highlighted.

for r in results:

        key = 0
        title = r['title']
        abstract = r['abstract']

        i, title = scanText(title)
        j, abstract = scanText(abstract)

        key = i + j		# number of non-redundant terms matched

        value = PROD_URL % (r['jnumID'], r['jnumID']) + ', ' + \
                r['short_citation'] + CRT + PB + \
                mgi_utils.prvalue(title) + PB + CRT + \
                mgi_utils.prvalue(abstract) + HR + CRT

        # store key:value pairs in dictionary
        if key not in ref:
                ref[key] = []
        ref[key].append(value)

        recs = recs + 1

# sort the keys and reverse the list so we can print the records
# out in descending order; those with the most hits print first

rkeys = list(ref.keys())
rkeys.sort()
rkeys.reverse()

for r in rkeys:
        for v in ref[r]:
                fp.write(v + CRT)
        
fp.write(PRE + 'Number of References:  %d' % (recs) + CRT)
fp.write('End Date/Time:  %s' % (mgi_utils.date()) + CRT)
fp.write('Server: %s, Database: %s' % (db.get_sqlServer(), db.get_sqlDatabase()) + CRT + EOP)
reportlib.finish_nonps(fp, isHTML = 1)
