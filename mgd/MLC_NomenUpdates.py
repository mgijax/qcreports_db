#!/usr/local/bin/python

'''
#
# Recent Nomenclature Events Report for MLC only
#
# Report:
#       template for creating Python reports
#
# Usage:
#       MLC_NomenUpdates.py
#
# Notes:
#	- all reports use db default of public login
#	- all reports use server/database default of environment
#	- use lowercase for all SQL commands (i.e. select not SELECT)
#	- all public SQL reports require the header and footer
#	- all private SQL reports require the header
#
# History:
#
# lec	01/04/99
#	- created
#
'''
 
import sys 
import os
import db
import mgi_html
import mgi_utils
import reportlib

#
# Main
#

currentReport = 'MLCNomenclature-current.html'

# remove current report link if it exists
if os.path.isfile('%s/%s' % (os.environ['QCREPORTOUTPUTDIR'], currentReport)):
	os.remove('%s/%s' % (os.environ['QCREPORTOUTPUTDIR'], currentReport))

# move existing Nomen reports to the archive
os.system('mv %s/MLCNomenclature-*.html %s' % (os.environ['QCREPORTOUTPUTDIR'], os.environ['QCNOMENARCHIVE']))

reportName = 'MLCNomenclature-' + mgi_utils.date('%Y-%m-%d')

if len(sys.argv) > 1:
	reportName = 'MLCNomenclature-' + sys.argv[1]
	currentDate = sys.argv[2]
else:
	reportName = 'MLCNomenclature-' + mgi_utils.date('%Y-%m-%d')
	currentDate = mgi_utils.date('%m/%d/%Y')

results = db.sql('select convert(varchar(25), dateadd(day, -7, "%s"))' % (currentDate), 'auto')
bdate = results[0]['']

results = db.sql('select convert(varchar(25), dateadd(day, 0, "%s"))' % (currentDate), 'auto')
edate = results[0]['']

title = 'Updates to MLC Mouse Nomenclature from %s to %s' % (bdate, edate)
fp = reportlib.init(reportName, title, os.environ['QCREPORTOUTPUTDIR'], isHTML = 1)

fp.write('J:23000 generally indicates gene family nomenclature revision event.\n\n')

cmd = []

cmd.append('select distinct h._Marker_key, m.symbol, name = substring(m.name,1,35), ' + \
'chromosome = substring(m.chromosome,1,2), ' + \
'c.sequenceNum, ' + \
'b.jnumID, author = substring(b._primary,1,16) ' + \
'into #markers ' + \
'from MRK_Marker m, MLC_Text mlc, MRK_History h, MRK_Chromosome c, BIB_All_View b ' + \
'where m._Species_key = 1 ' + \
'and m._Marker_key = h._History_key ' + \
'and h.event_date between dateadd(day, -7, "%s") ' % (currentDate) + \
'and dateadd(day, 1, "%s") ' % (currentDate) + \
'and h._Marker_key = mlc._Marker_key ' + \
'and m.chromosome = c.chromosome ' + \
'and m._Species_key = c._Species_key ' + \
'and h._Refs_key = b._Refs_key ')

cmd.append('create nonclustered index idx_key on #markers(_Marker_key)')

# get primary MGI ids (2)
cmd.append('select distinct m._Marker_key, a.accID ' + \
'from #markers m, MRK_Acc_View a ' + \
'where m._Marker_key = a._Object_key ' + \
'and a.prefixPart = "MGI:" ' + \
'and a._LogicalDB_key = 1 ' + \
'and a.preferred = 1')

# retrieve markers, sort (3)
cmd.append('select * from #markers order by sequenceNum, symbol')

results = db.sql(cmd, 'auto')

primaryID = {}
for r in results[2]:
	primaryID[r['_Marker_key']] = r['accID']

fp.write('%-2s %-25s %-35s %-10s %-16s\n' % ('Ch', 'Symbol', 'Gene Name', 'J#', 'First Author'))
fp.write('%-2s %-25s %-35s %-10s %-16s\n' % ('--', '------', '---------', '--', '------------'))

rows = 0
for r in results[3]:

	key = r['_Marker_key']
	symbol = mgi_html.escape(r['symbol'])

	fp.write('%-2s ' % (r['chromosome']))

	fp.write('%s%-25s%s ' % (reportlib.create_accession_anchor(primaryID[key]), symbol, reportlib.close_accession_anchor()))
	fp.write('%-35s ' % (r['name']))
	fp.write('%s%-10s%s ' % (reportlib.create_accession_anchor(r['jnumID']), r['jnumID'], reportlib.close_accession_anchor()))
	fp.write('%-20s ' % (r['author']))
	fp.write(reportlib.CRT)

	rows = rows + 1

fp.write(reportlib.CRT + '(%d rows affected)' % (rows) + reportlib.CRT)
reportlib.trailer(fp)
reportlib.finish_nonps(fp, isHTML = 1)	# non-postscript file

# re-create a symbolic link between the new file and the current file

os.chdir(os.environ['QCREPORTOUTPUTDIR'])
os.symlink(reportName + '.html', currentReport)

