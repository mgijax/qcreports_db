#!/usr/local/bin/python

'''
#
# TR 8747
#
# GXD Monthly Statistics
#
# Usage:
#       GXD_StatsMonthly.py
#
# Used by:
#
# Assumptions:  
#
# History:
#
# 04/30/2008	lec
#	- TR 8747; taken from GXD_Stats
#
'''
 
import sys
import os
import string
import db
import reportlib
import mgi_utils

CRT = reportlib.CRT

def monthlyCounts():

    #
    # Gene and Result counts by monthly period from startYear to endYear
    #

    # Gene stats by year/month

    db.sql('select year = datepart(year, a.creation_date), month = datepart(month, a.creation_date), ' + \
	'genes = count (distinct a._Marker_key),' + \
	'refs  = count (distinct a._Refs_key)' + \
    	'into #assayGenes ' + \
        'from GXD_Assay a ' + \
	'where a._AssayType_key in (1,2,3,4,5,6,8,9) ' + \
        'group by datepart(year, a.creation_date), datepart(month, a.creation_date)', None)

    db.sql('create index idx1 on #assayGenes(year)', None)
    db.sql('create index idx2 on #assayGenes(month)', None)

    #
    # Assay stats by year/month/assay type
    #

    db.sql('select year = datepart(year, a.creation_date), month = datepart(month, a.creation_date), ' + \
	'a._AssayType_key, ' + \
	'assays = count(*) ' + \
	'into #assays ' + \
	'from GXD_Assay a ' + \
	'where a._AssayType_key in (1,2,3,4,5,6,8,9) ' + \
	'group by datepart(year, a.creation_date), datepart(month, a.creation_date), a._AssayType_key', None)

    db.sql('create index idx1 on #assays(year)', None)
    db.sql('create index idx2 on #assays(month)', None)
    db.sql('create index idx3 on #assays(_AssayType_key)', None)

    #
    # Gel stats by year/month/assay type
    #

    db.sql('select year = datepart(year, a.creation_date), month = datepart(month, a.creation_date), ' + \
	'a._AssayType_key, ' + \
	'results = count(*) ' + \
	'into #gelresults ' + \
	'from GXD_Assay a, GXD_GelLane l, GXD_GelLaneStructure gls ' + \
	'where a._AssayType_key in (1,2,3,4,5,6,8,9) ' + \
	'and l._GelControl_key = 1 ' + \
	'and l._GelLane_key = gls._GelLane_key ' + \
	'group by datepart(year, a.creation_date), datepart(month, a.creation_date), a._AssayType_key', None)

    db.sql('create index idx1 on #gelresults(year)', None)
    db.sql('create index idx2 on #gelresults(month)', None)
    db.sql('create index idx3 on #gelresults(_AssayType_key)', None)

    #
    # InSitu stats by year/month/assay type
    #

    db.sql('select year = datepart(year, a.creation_date), month = datepart(month, a.creation_date), ' + \
	'a._AssayType_key, ' + \
	'results = count(*) ' + \
	'into #insituresults ' + \
	'from GXD_Assay a, GXD_Specimen s, GXD_InSituResult r, GXD_ISResultStructure rs ' + \
	'where a._AssayType_key in (1,2,3,4,5,6,8,9) ' + \
	'and a._Assay_key = s._Assay_key ' + \
	'and s._Specimen_key = r._Specimen_key ' + \
	'and r._Result_key = rs._Result_key ' + \
	'group by datepart(year, a.creation_date), datepart(month, a.creation_date), a._AssayType_key', None)

    db.sql('create index idx1 on #insituresults(year)', None)
    db.sql('create index idx2 on #insituresults(month)', None)
    db.sql('create index idx3 on #insituresults(_AssayType_key)', None)

    #
    # generate a list of all unique year/month values by the creation date of Assay records
    #

    db.sql('select distinct year = datepart(year, creation_date), ' + \
	'month = datepart(month, creation_date) into #periods from GXD_Assay', None)

    # initialize a table of periodCounts with all assay types for each year/month
    # and set "assays = 0", "results = 0"
    # subsequent updates will increment the assays and results counts

    db.sql('select p.year, p.month, t._AssayType_key, assayType = substring(t.assayType,1,25), ' + \
	'assays = 0, results = 0 ' + \
	'into #periodCounts ' +  \
	'from #periods p, GXD_AssayType t where t._AssayType_key > 0', None)

    # update the Assay count

    db.sql('update #periodCounts ' + \
	'set assays = a.assays ' + \
	'from #periodCounts p, #assays a ' + \
	'where a.year = p.year ' + \
	'and a.month = p.month ' + \
	'and a._AssayType_key = p._AssayType_key ', None)

    # update Gel Results count

    db.sql('update #periodCounts ' + \
	'set results = p.results + a.results ' + \
	'from #periodCounts p, #gelresults a ' + \
	'where a.year = p.year ' + \
	'and a.month = p.month ' + \
	'and a._AssayType_key = p._AssayType_key ', None)

    # update InSitu count

    db.sql('update #periodCounts ' + \
	'set results = p.results + a.results ' + \
	'from #periodCounts p, #insituresults a ' + \
	'where a.year = p.year ' + \
	'and a.month = p.month ' + \
	'and a._AssayType_key = p._AssayType_key ', None)

    db.sql('create index idx1 on #periodCounts(year)', None)
    db.sql('create index idx2 on #periodCounts(month)', None)
    db.sql('create index idx3 on #periodCounts(results)', None)

    #
    # Gene and Result counts by monthly period
    #

    fp.write(2*CRT + 'Gene and Result counts by monthly period:' + 2*CRT)
    fp.write(string.ljust('Year', 10))
    fp.write(string.ljust('Month', 10))
    fp.write(string.ljust('Genes', 10))
    fp.write(string.ljust('Results', 10))
    fp.write(string.ljust('References', 15) + CRT)
    fp.write(string.ljust('----', 10))
    fp.write(string.ljust('-----', 10))
    fp.write(string.ljust('------', 10))
    fp.write(string.ljust('-------', 10))
    fp.write(string.ljust('----------', 15) + CRT)

    #
    # assayGenes is 1-to-many with #periodCounts
    # use avg(gene) & avg(refs) to get a single value from #assayGenes
    #

    results = db.sql('select g.year, g.month, genes = avg(g.genes), results = sum(r.results), ref = avg(g.refs) ' + \
	'from #assayGenes g, #periodCounts r ' + \
	'where g.year = r.year ' + \
	'and g.month = r.month ' + \
	'group by g.year, g.month', 'auto')

    for r in results:
	fp.write(string.ljust(str(r['year']), 10))
	fp.write(string.ljust(str(r['month']), 10))
	fp.write(string.ljust(str(r['genes']), 10))
	fp.write(string.ljust(str(r['results']), 10))
	fp.write(string.ljust(str(r['ref']), 15) + CRT)

    #
    # Total Results
    #

    results = db.sql('select sum(results) from #periodCounts', 'auto')
    for r in results:
	fp.write(CRT + 'Total Results: ' + str(r['']) + CRT)

    #
    # Assays and results by Assay Type and month/year
    #

    fp.write(2*CRT + 'Assays and Results by Assay Type and Monthly Period:' + CRT)

    #
    # Cache sums by assay type
    #

    asummary = {}
    rsummary = {}
    results = db.sql('select assayType, asum = sum(assays), rsum = sum(results) ' + \
	'from #periodCounts group by assayType', 'auto')
    for r in results:
	asummary[r['assayType']] = r['asum']
	rsummary[r['assayType']] = r['rsum']

    results = db.sql('select assayType, year, month, assays, results ' + \
    	'from #periodCounts ' + \
    	'order by assayType, year, month', 'auto')

    fp.write(2*CRT + string.ljust('Assay Type', 30))
    fp.write(string.ljust('Year', 10))
    fp.write(string.ljust('Month', 10))
    fp.write(string.ljust('Assays', 10))
    fp.write(string.ljust('Results', 10) + CRT)
    fp.write(string.ljust('----------', 30))
    fp.write(string.ljust('----', 10))
    fp.write(string.ljust('-----', 10))
    fp.write(string.ljust('------', 10))
    fp.write(string.ljust('-------', 10) + CRT)

    prevAssay = ''
    for r in results:

	if len(prevAssay) > 0 and prevAssay != r['assayType']:
	    fp.write(CRT + 'Total Assays: ' + str(asummary[prevAssay]) + CRT)
	    fp.write('Total Results: ' + str(rsummary[prevAssay]) + CRT)
	    prevAssay = r['assayType']
            fp.write(2*CRT + string.ljust('Assay Type', 30))
            fp.write(string.ljust('Year', 10))
            fp.write(string.ljust('Month', 10))
            fp.write(string.ljust('Assays', 10))
            fp.write(string.ljust('Results', 10) + CRT)
            fp.write(string.ljust('----------', 30))
            fp.write(string.ljust('----', 10))
            fp.write(string.ljust('-----', 10))
            fp.write(string.ljust('------', 10))
            fp.write(string.ljust('-------', 10) + CRT)

	fp.write(string.ljust(r['assayType'], 30))
	fp.write(string.ljust(str(r['year']), 10))
	fp.write(string.ljust(str(r['month']), 10))
	fp.write(string.ljust(str(r['assays']), 10))
	fp.write(string.ljust(str(r['results']), 10) + CRT)
	prevAssay = r['assayType']

    fp.write(CRT + 'Total Assays: ' + str(asummary[prevAssay]) + CRT)
    fp.write('Total Results: ' + str(rsummary[prevAssay]) + CRT)


########
#      #
# Main #
#      #
########

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], sqlLogging = 1)
monthlyCounts()
reportlib.finish_nonps(fp)

