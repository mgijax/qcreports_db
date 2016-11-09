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
# 11/07/2016	sc
#	- TR12370 GXD HT Project
#	add HT experiment stats
#
# 04/28/2016	lec
#	- TR12026/added J:228563/lacz
#
# 01/08/2016	lec
#	- TR12223/gxd anatomy II
#
# 03/11/2014	lec
#	- TR11597/remove J:177549/EuReGene
#
# 09/17/2012
#	- TR11173/changed J:171498/"J Am Soc Nephrol" to "GUDMAP"
#
# 11/14/2011	lec
#	- TR10901; add J:177549/EuReGene
#
# 05/17/2011	lec
#	- TR10629; add J:171409
#
# 05/13/2010	lec
#	- TR10161; add J:157819
#
# 11/04/2009	lec
#	- TR 9936/TR9931; add J:153498
#
# 03/27/2009	mhall
#	- TR 9557, Exclude certian assay types
#
# 03/24/2009	lec
#	- TR 9526; add J:141291, J:143778
#
# 11/19/2008	lec
#	- TR 9365; added J:140465 Robson
#
# 05/20/2008
#	per Martin & Connie:
#	  remove "Number of Results (jpg attached)"
#	  remove "Number of Results (no jpg attached)"
#
# 10/18/2007	lec
#	- TR 8556; 
#	- Full Coded stats uses GXD_Expression; fixed the
#         "number of genes with GXD data" select statement
#
# 05/24/2006	lec
#	- TR 7694; imagesCount(); added "Number of Results...",
#	  "Number of Image Panes (no jpg attached)"
#
# 12/23/2004	lec
#       - adapted from GXD_Stats.sql and customSQL/expression/tr5521.py
# 
'''
 
import sys
import os
import string
import mgi_utils
import reportlib
import db

db.setTrace()
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

CRT = reportlib.CRT

startYear = 1998

# For GXD HT Experiments
gxdHtStartYear = 2016
endYear = string.atoi(mgi_utils.date('%Y'))

# electronic references
elect_ref1 = 'J:46439 Freeman, J:80502 Reymond, J:80501 Gitton, J:85124 Sousa-Nunes,'
elect_ref2 = 'J:91257 Gray, J:93300 Blackshaw, J:101679 Deltagen, J:122989 Eichele, J:140465 Robson'
elect_ref3 = 'J:141291 Tamplin1, J:143778 Tamplin2, J:153498 Eurexpress, J:157819 Blackshaw2, J:162220 BGEM'
elect_ref4 = 'J:171409 GUDMAP, J:228563 IMPC'

# _Refs_key for all electronic references
electronic = "(46734,81462,81463,86101,92242,94290,102744,124081,141558,142384,144871,154591,158912,163316,172505,229658)"


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
    cmd = '''
	insert into %s 
        select count(distinct(gi._Index_key)), %d 
        from GXD_Index gi, GXD_Index_Stages gis, VOC_Term vt 
        where gi._Index_key = gis._Index_key 
        and gis._IndexAssay_key = vt._Term_key 
        and vt._Vocab_key = 12 
        and vt.term %s '%s'
        and date_part('year', gi.creation_date) <= %d 
	''' % (table, year, op, value, year)
    return cmd

def cdnas():

    fp.write('cDNAs:' + 2*CRT)

    #
    # number of mouse cDNAs
    #

    db.sql('select _Source_key into temporary table mussource from PRB_Source where _Organism_key = 1', None)
    db.sql('create index mussource_idx on mussource(_Source_key)', None)

    db.sql('''select p._Probe_key 
        into temporary table cdnas
	from mussource s, PRB_Probe p 
	where s._Source_key = p._Source_key 
	and p._SegmentType_key = 63468 
	''', None)
    db.sql('create index cdnas_idx on cdnas(_Probe_key)', None)

    results = db.sql('select count(_Probe_key) as ccount from cdnas', 'auto')
    for r in results:
	fp.write('mouse cDNAs             : ' + str(r['ccount']) + CRT)

    #
    # number of markers curated to mouse cDNAs
    #

    results = db.sql('''
	select count(distinct(pm._Marker_key)) as mcount 
	from cdnas c, PRB_Marker pm 
	where c._Probe_key = pm._Probe_key
	''', 'auto')
    for r in results:
	fp.write('Markers curated to cDNAs:  ' + str(r['mcount']) + CRT)

def experiments():
    # 
    # Experiments
    #
    fp.write('%sHT Experiments:%s%s' % (CRT, CRT, CRT))
    fp.write(string.ljust('Year', 10))
    fp.write(string.ljust('Done', 10) + CRT)
    fp.write(string.ljust('-----', 10))
    fp.write(string.ljust('-----', 10) + CRT)

    for year in range(gxdHtStartYear, endYear + 1):
	results = db.sql('''select count(*) as expCt
	from GXD_HTExperiment
	where _CurationState_key = 20475421
	and date_part(\'year\', creation_date) <= %d ''' % (year), 'auto')
	for r in results:
	    fp.write(string.ljust(str(year), 10))
	    fp.write(string.ljust(str(r['expCt']), 10) + CRT)

def indexOnly():

    #
    #  These commands set-up the temp tables that will be used for building
    #  each of the parts of the report.
    #
    #  The first 3 are for Index, Reference and Gene counts
    #

    db.sql('select count(*) as idx_number, count(*) as year into temporary table indexcount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as ref_number, count(*) as year into temporary table referencecount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as gen_number, count(*) as year into temporary table markercount from BIB_Refs where 0=1', None)

    #
    #  We'll have one temp table for each assay type, with the exception of
    #  Prot-WM, Prot-sxn, RNA-WM and RNA-sxn.  These will be paired together.
    #

    db.sql('select count(*) as cdna_number, count(*) as year into temporary table cdnacount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as knkin_number, count(*) as year into temporary table knkincount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as nor_number, count(*) as year into temporary table norcount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as pri_number, count(*) as year into temporary table pricount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as prot_number, count(*) as year into temporary table protcount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as rna_number, count(*) as year into temporary table rnacount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as rnase_number, count(*) as year into temporary table rnasecount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as rtpcr_number, count(*) as year into temporary table rtpcrcount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as s1nuc_number, count(*) as year into temporary table s1nuccount from BIB_Refs where 0=1', None)
    db.sql('select count(*) as west_number, count(*) as year into temporary table westcount from BIB_Refs where 0=1', None)

    #
    #  Cycle through the years and fill each temp table with the cumulative
    #  statistics as of December 31st of that year.
    #

    for year in range(startYear, endYear + 1):

        #
        #  Fill Index temp table
        #
        db.sql('insert into indexcount select count(_Index_key), %d ' % (year) + \
               'from GXD_Index where date_part(\'year\', creation_date) <= %d ' % (year), None)

        #
        #  Fill Reference temp table
        #
        db.sql('insert into referencecount select count(distinct(_Refs_key)), %d ' % (year) + \
               'from GXD_Index where date_part(\'year\', creation_date) <= %d ' % (year), None)

        #
        #  Fill Gene temp table
        #
        db.sql('insert into markercount select count(distinct(_Marker_key)), %d ' % (year) + \
               'from GXD_Index where date_part(\'year\', creation_date) <= %d ' % (year), None)

        #
        #  Fill assay temp tables
        #
        db.sql(getAssayQuery('cdnacount', 'cDNA', '=', year), None)
        db.sql(getAssayQuery('knkincount', 'Knock in', '=', year), None)
        db.sql(getAssayQuery('norcount', 'Northern', '=', year), None)
        db.sql(getAssayQuery('pricount', 'Primer ex', '=', year), None)
        db.sql(getAssayQuery('protcount', 'Prot-%','like',  year), None)
        db.sql(getAssayQuery('rnacount', 'RNA-%','like',  year), None)
        db.sql(getAssayQuery('rnasecount', 'RNAse prot', '=', year), None)
        db.sql(getAssayQuery('rtpcrcount', 'RT-PCR', '=', year), None)
        db.sql(getAssayQuery('s1nuccount', 'S1 nuc', '=', year), None)
        db.sql(getAssayQuery('westcount', 'Western', '=', year), None)

    #
    #  Select out all of the rows from each temp table...
    #  ... then add them to a dictionary.
    #
    results = db.sql('select * from indexcount', 'auto')
    indx  = createDict(results,'year','idx_number')

    results = db.sql('select * from referencecount', 'auto')
    refs  = createDict(results,'year','ref_number')

    results = db.sql('select * from markercount', 'auto')
    gens  = createDict(results,'year','gen_number')

    results = db.sql('select * from cdnacount', 'auto')
    cdna  = createDict(results,'year','cdna_number')

    results = db.sql('select * from knkincount', 'auto')
    knkin = createDict(results,'year','knkin_number')

    results = db.sql('select * from norcount', 'auto')
    nor   = createDict(results,'year','nor_number')

    results = db.sql('select * from pricount', 'auto')
    pri   = createDict(results,'year','pri_number')

    results = db.sql('select * from protcount', 'auto')
    prot  = createDict(results,'year','prot_number')

    results = db.sql('select * from rnacount', 'auto')
    rna   = createDict(results,'year','rna_number')

    results = db.sql('select * from rnasecount', 'auto')
    rnase = createDict(results,'year','rnase_number')

    results = db.sql('select * from rtpcrcount', 'auto')
    rtpcr = createDict(results,'year','rtpcr_number')

    results = db.sql('select * from s1nuccount', 'auto')
    s1nuc = createDict(results,'year','s1nuc_number')

    results = db.sql('select * from westcount', 'auto')
    west  = createDict(results,'year','west_number')

    # Column headings #

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
    # Full Coded stats uses GXD_Expression
    #

    fp.write(2*CRT + 'GXD Assay and Results:' + 2*CRT)

    db.sql('''
	select _Assay_key, _Refs_key, _Marker_key, 'E'::text as source
	into temporary table gxd 
	from GXD_Expression where _Refs_key in %s
	and _AssayType_key in (1,2,3,4,5,6,8,9)
	''' % (electronic), None)
    db.sql('''
	insert into gxd select _Assay_key, _Refs_key, _Marker_key, 'L'::text as source
	from GXD_Expression where _Refs_key not in %s
	and _AssayType_key in (1,2,3,4,5,6,8,9)
	''' % (electronic), None)
    db.sql('create index gxd_idx1 on gxd(_Assay_key)', None)
    db.sql('create index gxd_idx2 on gxd(_Refs_key)', None)
    db.sql('create index gxd_idx3 on gxd(_Marker_key)', None)
    #db.sql('create index gxd_idx4 on gxd(source)', None)

    #
    # total number of references
    #

    results = db.sql('select count(distinct _Refs_key) as acount from gxd', 'auto')
    for r in results:
        fp.write('Assay References:  ' + str(r['acount']) + 2*CRT)

    #
    # Assays, Assay Results and Genes by source
    #

    fp.write('Assays and Assay Results by Source:' + CRT)
    fp.write('(Electronic References are:  ' + elect_ref1 + CRT)
    fp.write('                             ' + elect_ref2 + CRT)
    fp.write('                             ' + elect_ref3 + CRT)
    fp.write('                             ' + elect_ref4 + 2*CRT)

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

    results = db.sql("select count(distinct _Assay_key) as acount from gxd where source = 'E'", 'auto')
    for r in results:
        ecount = r['acount']

    results = db.sql("select count(distinct _Assay_key) as acount from gxd where source = 'L'", 'auto')
    for r in results:
        lcount = r['acount']

    fp.write(string.ljust('Assays', 15))
    fp.write(string.ljust(str(ecount), 25))
    fp.write(string.ljust(str(lcount), 25))
    fp.write(string.ljust(str(ecount + lcount), 10) + CRT)

    #
    # Results
    #

    results = db.sql("select count(_Assay_key) as acount from gxd where source = 'E'", 'auto')
    for r in results:
        ecount = r['acount']

    results = db.sql("select count(_Assay_key) as acount from gxd where source = 'L'", 'auto')
    for r in results:
        lcount = r['acount']

    fp.write(string.ljust('Assay Results', 15))
    fp.write(string.ljust(str(ecount), 25))
    fp.write(string.ljust(str(lcount), 25))
    fp.write(string.ljust(str(ecount + lcount), 10) + CRT)

    #
    # Genes
    #

    results = db.sql('''
	select count(distinct _Marker_key) as genes
    	from GXD_Expression where _AssayType_key in (1,2,3,4,5,6,8,9)
	''', 'auto')
    fp.write(2*CRT + 'Number of genes with GXD data:  ' + str(results[0]['genes']) + CRT)

def mutantAlleles():

    #
    # number of mutant alleles in GXD
    #

    results = db.sql('''
	select count(distinct a._Allele_key) as acount
	from GXD_AlleleGenotype g, ALL_Allele a 
	where g._Allele_key = a._Allele_key 
	and a.isWildType != 1 
	and exists (select 1 from GXD_Expression e 
	where g._Genotype_key = e._Genotype_key and _AssayType_key in (1,2,3,4,5,6,8,9)) 
	and a.symbol not like '%<+>%'
	''', 'auto')

    for r in results:
        fp.write('Number of mutant alleles that have GXD data:  ' + str(r['acount']) + CRT)

def imageCounts():

    #
    # number of full-coded papers with images (jpegs attached)
    # number of full-coded papers with images (jpegs not attached)
    #
    # those that are annotated to images and the image has dimensions
    # (which means there is a jpeg file)
    # 
    # those that are annotated to images and the image has no dimensions
    # (which means there is not a jpeg file)
    # 

    db.sql('''
	(
	select distinct a._Refs_key 
	into temporary table images 
        from GXD_Assay a, IMG_Image i, IMG_ImagePane p 
        where a._AssayType_key in (1,2,3,4,5,6,8,9) and 
	    a._ImagePane_key = p._ImagePane_key and 
            p._Image_key = i._Image_key and 
            i.xDim is not NULL 
        union 
        select distinct a._Refs_key 
        from GXD_Assay a, GXD_Specimen g, GXD_ISResultImage_View r 
        where a._AssayType_key in (1,2,3,4,5,6,8,9) and 
            a._Assay_key = g._Assay_key and 
            g._Specimen_key = r._Specimen_key and 
            r.xDim is not NULL
	)
	''', None)

    db.sql('create index images_idx1 on images(_Refs_key)', None)

    results = db.sql('select count(_Refs_key) as acount from images', 'auto')
    for r in results:
        fp.write('Number of full coded papers with Images:  ' + str(r['acount']) + CRT)

    #
    # TR12279/sync with mgihome/homepages/stats/all_stats.shtml#allstats_gxd
    # if this SQL changes, then update the SQL here:
    #   select * from MGI_StatisticSQL where _Statistic_key = 31;
    # see script in /mgi/all/wts_projects/12200/12279
    #

    db.sql('''
	(
	select distinct ip._ImagePane_key 
	into temporary table imagepanes1 
	from IMG_ImagePane ip, IMG_Image i, GXD_Assay a 
	where ip._Image_key = i._Image_key 
	and i.xDim is not null 
	and ip._ImagePane_key = a._ImagePane_key 
	and a._AssayType_key in (1,2,3,4,5,6,8,9) 
	union  
	select distinct ip._ImagePane_key 
	from IMG_ImagePane ip, IMG_Image i, GXD_InSituResultImage isri, GXD_InSituResult isr,  
	     GXD_Specimen s, GXD_Assay a 
	where ip._Image_key = i._Image_key 
	and i.xDim is not null 
	and ip._ImagePane_key = isri._ImagePane_key 
	and isri._Result_key = isr._Result_key 
	and isr._Specimen_key = s._Specimen_key 
	and s._Assay_key = a._Assay_key 
	and a._AssayType_key in (1,2,3,4,5,6,8,9) 
	)
	''', None)

    results = db.sql('select count(distinct _ImagePane_key) as acount from imagepanes1', 'auto')
    for r in results:
        fp.write('Number of Image Panes (jpg attached):  ' + str(r['acount']) + CRT)

    db.sql('''
	select distinct ip._ImagePane_key 
	into temporary table imagepanes2 
	from IMG_ImagePane ip, IMG_Image i, GXD_Assay a 
	where ip._Image_key = i._Image_key 
	and i.xDim is null 
	and ip._ImagePane_key = a._ImagePane_key 
	and a._AssayType_key in (1,2,3,4,5,6,8,9) 
	union  
	select distinct ip._ImagePane_key 
	from IMG_ImagePane ip, IMG_Image i, GXD_InSituResultImage isri, GXD_InSituResult isr,  
	     GXD_Specimen s, GXD_Assay a 
	where ip._Image_key = i._Image_key 
	and i.xDim is null 
	and ip._ImagePane_key = isri._ImagePane_key 
	and isri._Result_key = isr._Result_key 
	and isr._Specimen_key = s._Specimen_key 
	and s._Assay_key = a._Assay_key 
	and a._AssayType_key in (1,2,3,4,5,6,8,9) 
	''', None)

    results = db.sql('select count(distinct _ImagePane_key) as acount from imagepanes2', 'auto')
    for r in results:
        fp.write('Number of Image Panes (no jpg attached):  ' + str(r['acount']) + CRT)

def assayTypeCounts():

    #
    # Build a temp table to get the gene and assay counts.
    #
    db.sql('''
	select _Assay_key, _AssayType_key, _Marker_key, 'L'::text as source
        into temporary table gxdcounts 
        from GXD_Expression 
        where isForGXD = 1 and _Refs_key not in %s
        and _AssayType_key in (1,2,3,4,5,6,8,9)
	''' % (electronic), None)

    db.sql('''
	insert into gxdcounts 
        select _Assay_key, _AssayType_key, _Marker_key, 'E'::text as source
        from GXD_Expression 
        where isForGXD = 1 and _Refs_key in %s 
        and _AssayType_key in (1,2,3,4,5,6,8,9)
	''' % (electronic), None)

    db.sql('create index gxdcounts_idx1 on gxdcounts(_Assay_key)', None)
    db.sql('create index gxdcounts_idx2 on gxdcounts(_AssayType_key)', None)
    db.sql('create index gxdcounts_idx3 on gxdcounts(_Marker_key)', None)
    db.sql('create index gxdcounts_idx4 on gxdcounts(source)', None)

    #
    # Get the gene and assay counts from the temp table.
    #
    cmd = []
    cmd.append('''
	select _AssayType_key, count(distinct _Marker_key) as counter
        from gxdcounts 
        group by _AssayType_key
	''')
    cmd.append('''
	select _AssayType_key, count(distinct _Assay_key) as counter
        from gxdcounts 
        where source = 'L' 
        group by _AssayType_key
	''')
    cmd.append('''
	select _AssayType_key, count(distinct _Assay_key) as counter
        from gxdcounts 
        where source = 'E' 
        group by _AssayType_key
	''')
    results = db.sql(cmd,'auto')

    #
    # Add the gene counts for each assay type to a dictionary.
    #
    genes = {}
    for r in results[0]:
        genes[r['_AssayType_key']] = r['counter']

    #
    # Add the assay counts (literature and electronic submissions) for each
    # assay type to dictionaries.
    #
    assayLiter = {}
    for r in results[1]:
        assayLiter[r['_AssayType_key']] = r['counter']

    assayElect = {}
    for r in results[2]:
        assayElect[r['_AssayType_key']] = r['counter']

    #
    # Get the result counts from the GXD_Expression table.
    #
    cmd = []
    cmd.append('''
	select _AssayType_key, count(_Assay_key) as counter
        from GXD_Expression 
        where isForGXD = 1 and _Refs_key not in %s 
        and _AssayType_key in (1,2,3,4,5,6,8,9)
        group by _AssayType_key
	''' % (electronic))
    cmd.append('''
	select _AssayType_key, count(_Assay_key) as counter
        from GXD_Expression 
        where isForGXD = 1 and _Refs_key in %s 
        and _AssayType_key in (1,2,3,4,5,6,8,9)
        group by _AssayType_key
	''' % (electronic))
    results = db.sql(cmd,'auto')

    #
    # Add the result counts (literature and electronic submission) for each
    # assay type to dictionaries.
    #
    resLiter = {}
    for r in results[0]:
        resLiter[r['_AssayType_key']] = r['counter']

    resElect = {}
    for r in results[1]:
        resElect[r['_AssayType_key']] = r['counter']

    #
    # Get the assay types in the order that they should appear in the
    # report.  Also get the key for each assay to use as a lookup to get
    # the counts for each assay.
    #
    results = db.sql('''
	select _AssayType_key, assayType 
        from GXD_AssayType 
        where _AssayType_key > 0 
	and _AssayType_key in (1,2,3,4,5,6,8,9) 
        order by assayType
	''','auto')
    
    #
    # Print a heading for this section of the report.
    #
    fp.write(2*CRT + 'Number of Genes, Assays and Results by Assay Type:' + 2*CRT)

    fp.write(string.ljust(' ', 40))
    fp.write(string.ljust('Assay', 10))
    fp.write(string.ljust('Assay', 12))
    fp.write(string.ljust('Assay', 12))
    fp.write(string.ljust('Results', 10))
    fp.write(string.ljust('Results', 12))
    fp.write(string.ljust('Results', 12) + CRT)

    fp.write(string.ljust('Assay Type', 30))
    fp.write(string.ljust('Genes', 10))
    fp.write(string.ljust('Total', 10))
    fp.write(string.ljust('Literature', 12))
    fp.write(string.ljust('Submitted', 12))
    fp.write(string.ljust('Total', 10))
    fp.write(string.ljust('Literature', 12))
    fp.write(string.ljust('Submitted', 12) + CRT)

    fp.write(string.ljust('----------------------------', 30))
    fp.write(string.ljust('--------', 10))
    fp.write(string.ljust('--------', 10))
    fp.write(string.ljust('----------', 12))
    fp.write(string.ljust('----------', 12))
    fp.write(string.ljust('--------', 10))
    fp.write(string.ljust('----------', 12))
    fp.write(string.ljust('----------', 12) + CRT)

    #
    # Loop through each assay type and print the counts for the report.
    #
    for r in results:
        assayType = r['assayType']
        assayTypeKey = r['_AssayType_key']

        if genes.has_key(assayTypeKey):
            geneCount = genes[assayTypeKey]
        else:
            geneCount = 0

        if assayLiter.has_key(assayTypeKey):
            assayLiterCount = assayLiter[assayTypeKey]
        else:
            assayLiterCount = 0

        if assayElect.has_key(assayTypeKey):
            assayElectCount = assayElect[assayTypeKey]
        else:
            assayElectCount = 0

        if resLiter.has_key(assayTypeKey):
            resLiterCount = resLiter[assayTypeKey]
        else:
            resLiterCount = 0

        if resElect.has_key(assayTypeKey):
            resElectCount = resElect[assayTypeKey]
        else:
            resElectCount = 0

        fp.write(string.ljust(assayType, 30))
        fp.write(string.ljust(str(geneCount), 10))
        fp.write(string.ljust(str(assayLiterCount+assayElectCount), 10))
        fp.write(string.ljust(str(assayLiterCount), 12))
        fp.write(string.ljust(str(assayElectCount), 12))
        fp.write(string.ljust(str(resLiterCount+resElectCount), 10))
        fp.write(string.ljust(str(resLiterCount), 12))
        fp.write(string.ljust(str(resElectCount), 12) + CRT)

########
#      #
# Main #
#      #
########

fp = reportlib.init(sys.argv[0], outputdir = os.environ['QCOUTPUTDIR'], sqlLogging = 1,
	fileExt = '.' + os.environ['DATE'] + '.rpt')
cdnas()
experiments()
indexOnly()
fullCoded()
mutantAlleles()
imageCounts()
assayTypeCounts()
reportlib.finish_nonps(fp)

