#!/usr/local/bin/python

'''
#
# TR 6440/5521
#
# GXD Statistics
#
# Usage:
#       GXD_Stats.py
#
# Used by:
#
# Assumptions:  
#
# History:
#
# lec    12/23/2004
#       - adapted from GXD_Stats.sql and customSQL/expression/tr5521.py
# 
'''
 
import sys
import os
import string
import db
import reportlib
import mgi_utils

CRT = reportlib.CRT

startYear = 1998
endYear = string.atoi(mgi_utils.date('%Y'))

#############
#           #
# Functions #
#           #
#############

'''
# requires: results,    The array of data
#           keyField,   The name of the key to use to 
#                       create the dictionary entries
#           valueField, The name of the row field to use
#                       as the value for the dictionary entry
# effects:
#     Creates a dictionary from a result array from db.sql
#     using the keyfield as the key and 
#     the value field as the key value.
#
# returns:
#     a dictionary
'''
def createDict(results, keyField, valueField):
    d = {}
    for r in results:
        key = r[keyField]
        value = r[valueField]
        if not d.has_key(key):
            d[key] = value
    return d

def getAssayQuery(table, value, op, year):
    cmd = 'insert %s ' % (table) + \
          'select count(distinct(gi._Index_key)), %d ' % (year) + \
          'from GXD_Index gi, GXD_Index_Stages gis, VOC_Term vt ' + \
          'where gi._Index_key = gis._Index_key ' + \
          'and gis._IndexAssay_key = vt._Term_key ' + \
          'and vt._Vocab_key = 12 ' + \
          'and vt.term %s "%s" ' % (op, value) + \
          'and datepart(year, gi.creation_date) <= %d ' % (year)
    return cmd

def cdnas():

    fp.write('cDNAs:' + 2*CRT)

    #
    # number of mouse cDNAs
    #

    db.sql('select _Source_key into #mussource from PRB_Source where _Organism_key = 1', None)
    db.sql('create index idx1 on #mussource(_Source_key)', None)

    db.sql('select p._Probe_key into #cdnas ' + \
	'from #mussource s, PRB_Probe p ' + \
	'where s._Source_key = p._Source_key ' + \
	'and p._SegmentType_key = 63468 ', None)
    db.sql('create index idx1 on #cdnas(_Probe_key)', None)

    results = db.sql('select ccount = count(_Probe_key) from #cdnas', 'auto')
    for r in results:
	fp.write('mouse cDNAs             : ' + str(r['ccount']) + CRT)

    #
    # number of markers curated to mouse cDNAs
    #

    results = db.sql('select mcount = count(distinct(pm._Marker_key)) ' + \
	'from #cdnas c, PRB_Marker pm ' + \
	'where c._Probe_key = pm._Probe_key', 'auto')
    for r in results:
	fp.write('Markers curated to cDNAs:  ' + str(r['mcount']) + CRT)

def indexOnly():

    #
    #  These commands set-up the temp tables that will be used for building
    #  each of the parts of the report.
    #
    #  The first 3 are for Index, Reference and Gene counts
    #

    db.sql('select count(*) as idx_number, count(*) as year into #indexcount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as ref_number, count(*) as year into #referencecount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as gen_number, count(*) as year into #markercount from BIB_Refs where 0=1', None)

    #
    #  We'll have one temp table for each assay type, with the exception of
    #  Prot-WM, Prot-sxn, RNA-WM and RNA-sxn.  These will be paired together.
    #

    db.sql('select count(*) as cdna_number, count(*) as year into #cdnacount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as knkin_number, count(*) as year into #knkincount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as nor_number, count(*) as year into #norcount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as pri_number, count(*) as year into #pricount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as prot_number, count(*) as year into #protcount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as rna_number, count(*) as year into #rnacount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as rnase_number, count(*) as year into #rnasecount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as rtpcr_number, count(*) as year into #rtpcrcount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as s1nuc_number, count(*) as year into #s1nuccount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as west_number, count(*) as year into #westcount from BIB_Refs where 0=1', None)

    #
    #  Cycle through the years and fill each temp table with the cumulative
    #  statistics as of December 31st of that year.
    #

    for year in range(startYear, endYear):

        #
        #  Fill Index temp table
        #
        db.sql('insert #indexcount select count(_Index_key), %d ' % (year) + \
               'from GXD_Index where datepart(year, creation_date) <= %d ' % (year), None)

        #
        #  Fill Reference temp table
        #
        db.sql('insert #referencecount select count(distinct(_Refs_key)), %d ' % (year) + \
               'from GXD_Index where datepart(year, creation_date) <= %d ' % (year), None)

        #
        #  Fill Gene temp table
        #
        db.sql('insert #markercount select count(distinct(_Marker_key)), %d ' % (year) + \
               'from GXD_Index where datepart(year, creation_date) <= %d ' % (year), None)

        #
        #  Fill assay temp tables
        #
        db.sql(getAssayQuery('#cdnacount', 'cDNA', '=', year), None)
        db.sql(getAssayQuery('#knkincount', 'Knock in', '=', year), None)
        db.sql(getAssayQuery('#norcount', 'Northern', '=', year), None)
        db.sql(getAssayQuery('#pricount', 'Primer ex', '=', year), None)
        db.sql(getAssayQuery('#protcount', 'Prot-%','like',  year), None)
        db.sql(getAssayQuery('#rnacount', 'RNA-%','like',  year), None)
        db.sql(getAssayQuery('#rnasecount', 'RNAse prot', '=', year), None)
        db.sql(getAssayQuery('#rtpcrcount', 'RT-PCR', '=', year), None)
        db.sql(getAssayQuery('#s1nuccount', 'S1 nuc', '=', year), None)
        db.sql(getAssayQuery('#westcount', 'Western', '=', year), None)

    #
    #  Select out all of the rows from each temp table...
    #  ... then add them to a dictionary.
    #
    results = db.sql('select * from #indexcount', 'auto')
    indx  = createDict(results,'year','idx_number')

    results = db.sql('select * from #referencecount', 'auto')
    refs  = createDict(results,'year','ref_number')

    results = db.sql('select * from #markercount', 'auto')
    gens  = createDict(results,'year','gen_number')

    results = db.sql('select * from #cdnacount', 'auto')
    cdna  = createDict(results,'year','cdna_number')

    results = db.sql('select * from #knkincount', 'auto')
    knkin = createDict(results,'year','knkin_number')

    results = db.sql('select * from #norcount', 'auto')
    nor   = createDict(results,'year','nor_number')

    results = db.sql('select * from #pricount', 'auto')
    pri   = createDict(results,'year','pri_number')

    results = db.sql('select * from #protcount', 'auto')
    prot  = createDict(results,'year','prot_number')

    results = db.sql('select * from #rnacount', 'auto')
    rna   = createDict(results,'year','rna_number')

    results = db.sql('select * from #rnasecount', 'auto')
    rnase = createDict(results,'year','rnase_number')

    results = db.sql('select * from #rtpcrcount', 'auto')
    rtpcr = createDict(results,'year','rtpcr_number')

    results = db.sql('select * from #s1nuccount', 'auto')
    s1nuc = createDict(results,'year','s1nuc_number')

    results = db.sql('select * from #westcount', 'auto')
    west  = createDict(results,'year','west_number')

    ###################
    # Column headings #
    ###################

    #
    #  We'll start by printing out a table for the index, reference and gene statistics.
    #

    fp.write(2*CRT + 'GXD Index Stats:' + 2*CRT)
    fp.write(string.ljust('Year', 10))
    fp.write(string.ljust('Index', 10))
    fp.write(string.ljust('Refs', 10))
    fp.write(string.ljust('Genes', 10) + CRT)
    fp.write(string.ljust('-----', 10))
    fp.write(string.ljust('-----', 10))
    fp.write(string.ljust('-----', 10))
    fp.write(string.ljust('-----', 10) + CRT)

    keys = indx.keys()
    keys.sort()
    for key in keys:
        if key > 0:
            fp.write(string.ljust(str(key), 10))
            fp.write(string.ljust(str(indx[key]), 10))
            fp.write(string.ljust(str(refs[key]), 10))
            fp.write(string.ljust(str(gens[key]), 10) + CRT)
    fp.write(CRT)

    #
    #  Now build the assay part of the report
    #
    #  First the header...
    #
    fp.write('Number of Assays in GXD Index by Assay Type' + 2*CRT)
    fp.write(string.ljust('As of 12/31', 15))
    fp.write(string.ljust('cDNA', 10))
    fp.write(string.ljust('Knock', 10))
    fp.write(string.ljust('North', 10))
    fp.write(string.ljust('Prime', 10))
    fp.write(string.ljust('Immuno', 10))
    fp.write(string.ljust('RNA', 10))
    fp.write(string.ljust('RNAse', 10))
    fp.write(string.ljust('RTPCR', 10))
    fp.write(string.ljust('S1nuc', 10))
    fp.write(string.ljust('West', 10) + CRT)
    fp.write(string.ljust('-----------', 15))
    fp.write(string.ljust('------', 10))
    fp.write(string.ljust('------', 10))
    fp.write(string.ljust('------', 10))
    fp.write(string.ljust('------', 10))
    fp.write(string.ljust('------', 10))
    fp.write(string.ljust('------', 10))
    fp.write(string.ljust('------', 10))
    fp.write(string.ljust('------', 10))
    fp.write(string.ljust('------', 10))
    fp.write(string.ljust('------', 10) + CRT)

    #
    #  Cycle through the years in each of the assay dictionaries.
    #
    for key in keys:
        if key > 0:
            #
            #  Add the year value column to the output.
            #
	    fp.write(string.ljust(str(key), 15))
            fp.write(string.ljust(str(cdna[key]), 10))
            fp.write(string.ljust(str(knkin[key]), 10))
            fp.write(string.ljust(str(nor[key]), 10))
            fp.write(string.ljust(str(pri[key]), 10))
            fp.write(string.ljust(str(prot[key]), 10))
            fp.write(string.ljust(str(rna[key]), 10))
            fp.write(string.ljust(str(rnase[key]), 10))
            fp.write(string.ljust(str(rtpcr[key]), 10))
            fp.write(string.ljust(str(s1nuc[key]), 10))
            fp.write(string.ljust(str(west[key]), 10) + CRT)

def fullCoded():

    #
    # Full Coded stats using GXD_Expression cache
    #

    fp.write(2*CRT + 'GXD Assay and Results:' + 2*CRT)

    #
    # select assays by source (electronic vs. literature)
    #  J:46439 Freeman 32476 results in 706 assays
    #  J:80502 Reymond 15220 results in 403 assays
    #  J:80501 Gitton 116 results in 269 assays
    #  J:85124 Sousa-Nunes 455 results in 32 assays
    #  J:91257 Gray 37841 results in 2769 assays

    electronic = "(46734,81462,81463,86101,92242)"
    db.sql('select _Assay_key, _Refs_key, _Marker_key, source = "E" into #gxd ' + \
	'from GXD_Expression where _Refs_key in %s' % (electronic), None)
    db.sql('insert into #gxd select _Assay_key, _Refs_key, _Marker_key, source = "L" ' + \
	'from GXD_Expression where _Refs_key not in %s' % (electronic), None)
    db.sql('create index idx1 on #gxd(_Assay_key)', None)
    db.sql('create index idx2 on #gxd(_Refs_key)', None)
    db.sql('create index idx3 on #gxd(_Marker_key)', None)
    db.sql('create index idx4 on #gxd(source)', None)

    #
    # total number of references
    #

    results = db.sql('select acount = count(distinct _Refs_key) from #gxd', 'auto')
    for r in results:
        fp.write('Assay References:  ' + str(r['acount']) + 2*CRT)

    #
    # Assays, Assay results and genes by source
    #

    fp.write('Assays, Assay results and genes by source:' + 2*CRT)
    fp.write(string.ljust('             ', 15))
    fp.write(string.ljust('Electronic Submission', 25))
    fp.write(string.ljust('Literature Submission', 25))
    fp.write(string.ljust('Total', 10) + CRT)
    fp.write(string.ljust('-------------', 15))
    fp.write(string.ljust('---------------------', 25))
    fp.write(string.ljust('---------------------', 25))
    fp.write(string.ljust('-----', 10) + CRT)

    #
    # Assays 
    #

    results = db.sql('select count(distinct _Assay_key) from #gxd where source = "E"', 'auto')
    for r in results:
        ecount = r['']

    results = db.sql('select count(distinct _Assay_key) from #gxd where source = "L"', 'auto')
    for r in results:
        lcount = r['']

    fp.write(string.ljust('Assays', 15))
    fp.write(string.ljust(str(ecount), 25))
    fp.write(string.ljust(str(lcount), 25))
    fp.write(string.ljust(str(ecount + lcount), 10) + CRT)

    #
    # Results
    #

    results = db.sql('select count(_Assay_key) from #gxd where source = "E"', 'auto')
    for r in results:
        ecount = r['']

    results = db.sql('select count(_Assay_key) from #gxd where source = "L"', 'auto')
    for r in results:
        lcount = r['']

    fp.write(string.ljust('Assay Results', 15))
    fp.write(string.ljust(str(ecount), 25))
    fp.write(string.ljust(str(lcount), 25))
    fp.write(string.ljust(str(ecount + lcount), 10) + CRT)

    #
    # Genes
    #

    results = db.sql('select count(distinct _Marker_key) from #gxd where source = "E"', 'auto')
    for r in results:
        ecount = r['']

    results = db.sql('select count(distinct _Marker_key) from #gxd where source = "L"', 'auto')
    for r in results:
        lcount = r['']

    fp.write(string.ljust('Genes', 15))
    fp.write(string.ljust(str(ecount), 25))
    fp.write(string.ljust(str(lcount), 25))
    fp.write(string.ljust(str(ecount + lcount), 10) + CRT)

def mutantAlleles():

    #
    # number of mutant alleles in GXD
    #

    results = db.sql('select acount = count(distinct a._Allele_key) ' + \
	'from GXD_AlleleGenotype g, ALL_Allele a ' + \
	'where g._Allele_key = a._Allele_key ' + \
	'and exists (select 1 from GXD_Expression e ' + \
	'where g._Genotype_key = e._Genotype_key) ' + \
	'and a.symbol not like "%<+>%"', 'auto')

    for r in results:
        fp.write(2*CRT + 'Number of mutant alleles that have GXD data:  ' + str(r['acount']) + CRT)

def withImages():

    #
    # number of full-coded papers with images (jpegs)
    #
    # those that are annotated to images and the image has dimensions
    # (which means there is a jpeg file)
    # 

    db.sql('select distinct a._Refs_key into #images ' + \
      'from GXD_Assay a, IMG_Image i, IMG_ImagePane p ' + \
      'where a._ImagePane_key = p._ImagePane_key and ' + \
            'p._Image_key = i._Image_key and ' + \
            'i.xDim is not NULL ' + \
      'union ' + \
      'select distinct a._Refs_key ' + \
      'from GXD_Assay a, GXD_Specimen g, GXD_ISResultImage_View r ' + \
      'where a._Assay_key = g._Assay_key and ' + \
            'g._Specimen_key = r._Specimen_key and ' + \
            'r.xDim is not NULL ', None)

    db.sql('create index idx1 on #images(_Refs_key)', None)

    results = db.sql('select acount = count(_Refs_key) from #images', 'auto')
    for r in results:
        fp.write('Number of full coded papers with Images:  ' + str(r['acount']) + 2*CRT)

def monthlyCounts():

    #
    # Gene and Result counts by monthly period from startYear to endYear
    #

    # Gene stats by year/month

    db.sql('select year = datepart(year, creation_date), ' + \
	'month = datepart(month, creation_date), ' + \
	'genes = count (distinct _Marker_key),' + \
	'refs  = count (distinct _Refs_key)' + \
    	'into #assayGenes ' + \
        'from GXD_Assay ' + \
        'group by datepart(year, creation_date), datepart(month, creation_date)', None)

    db.sql('create index idx1 on #assayGenes(year)', None)
    db.sql('create index idx2 on #assayGenes(month)', None)

    #
    # Assay stats by year/month/assay type
    #

    db.sql('select year = datepart(year, creation_date), ' + \
	'month = datepart(month, creation_date), ' + \
	'_AssayType_key, assays = count(*) ' + \
	'into #assays ' + \
	'from GXD_Assay ' + \
	'group by datepart(year, creation_date), datepart(month, creation_date), _AssayType_key', None)

    db.sql('create index idx1 on #assays(year)', None)
    db.sql('create index idx2 on #assays(month)', None)
    db.sql('create index idx3 on #assays(_AssayType_key)', None)

    #
    # Gel stats by year/month/assay type
    #

    db.sql('select year = datepart(year, a.creation_date), ' + \
	'month = datepart(month, a.creation_date), ' + \
	'a._AssayType_key, results = count(*) ' + \
	'into #gelresults ' + \
	'from GXD_Assay a, GXD_GelLane l, GXD_GelLaneStructure gls ' + \
	'where a._Assay_key = l._Assay_key ' + \
	'and l._GelControl_key = 1 ' + \
	'and l._GelLane_key = gls._GelLane_key ' + \
	'group by datepart(year, a.creation_date), datepart(month, a.creation_date), a._AssayType_key', None)

    db.sql('create index idx1 on #gelresults(year)', None)
    db.sql('create index idx2 on #gelresults(month)', None)
    db.sql('create index idx3 on #gelresults(_AssayType_key)', None)

    #
    # InSitu stats by year/month/assay type
    #

    db.sql('select year = datepart(year, a.creation_date), ' + \
	'month = datepart(month, a.creation_date), ' + \
	'a._AssayType_key, results = count(*) ' + \
	'into #insituresults ' + \
	'from GXD_Assay a, GXD_Specimen s, GXD_InSituResult r, GXD_ISResultStructure rs ' + \
	'where a._Assay_key = s._Assay_key ' + \
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

    # initialize a table with all assay types for each year/month
    # and set "assays = 0", "results = 0"
    # subsequenct updates will increment the assays and results counts

    db.sql('select p.year, p.month, t._AssayType_key, assayType = substring(t.assayType,1,25), assays = 0, results = 0 ' + \
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

   # remove any assay types for which we have no results */
#delete #periodCounts
#from #periodCounts p
#where exists ( select 1 from #periodCounts pc
#where p._AssayType_key = pc._AssayType_key
#group by pc._AssayType_key
#having sum (pc.Assays) = 0)

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

    results = db.sql('select g.year, g.month, genes = avg(g.genes), results = sum(r.results), ref = avg (g.refs) ' + \
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

    fp.write(2*CRT + 'Assays and results by Assay-Type and monthly period:' + CRT)

    #
    # Cache sums by assay type
    #

    asummary = {}
    rsummary = {}
    results = db.sql('select assayType, asum = sum(assays), rsum = sum(results) from #periodCounts group by assayType', 'auto')
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
cdnas()
indexOnly()
fullCoded()
mutantAlleles()
withImages()
monthlyCounts()
reportlib.trailer(fp)
reportlib.finish_nonps(fp)

