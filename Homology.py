#!/usr/local/bin/python

'''
#
# Homology.py 11/16/98
#
# Report:
#       Detail information for Homology record
#
# Usage:
#       Homology.py command
#
#       where:
#
#       command = SQL select statement which returns the 
#                 desired Homology records from the database.
#                 The classRef, short_citation and jnum columns 
#                 must be included in the select statement.
#
# Generated from:
#       Editing Interface, Homology Report form
#
# Notes:
#	Produces a postscript output file.
#
# History:
#
# lec	01/13/98
#	- added comments
#
'''
 
import sys
import os
import string
import mgdlib
import reportlib

CRT = reportlib.CRT
TAB = reportlib.TAB

def parse_homology(homology):
	
	fp.write(TAB + mgdlib.prvalue(homology['species']) + TAB + \
		 mgdlib.prvalue(homology['symbol']) + TAB + \
		 mgdlib.prvalue(homology['chromosome']))
	fp.write(TAB + mgdlib.prvalue(homology['offset']))
	fp.write(TAB + mgdlib.prvalue(homology['name']))

	try:
		fp.write(CRT + TAB + mgdlib.prvalue(homology['accID']))
	except:
		pass

	fp.write(CRT)

def parse_reference(reference):

	[classKey, refKey] = string.splitfields(reference['classRef'], ':')

	fp.write(2*CRT + mgdlib.prvalue(reference['short_citation']) + TAB + \
		 mgdlib.prvalue(reference['jnum']) + CRT)

	# Retrieve Mouse Markers 

	cmd = '''select distinct
	      m._Species_key, m.species, m.symbol, m.name, m.chromosome,
	      m.offset, accID = m.mgiID 
              from HMD_Homology h, HMD_Homology_Marker hm, MRK_Mouse_View m
	      where h._Class_key = %s and h._Refs_key = %s
	      and h._Homology_key = hm._Homology_key
	      and hm._Marker_key = m._Marker_key order by _Species_key
	      ''' % (classKey, refKey)
	mgdlib.sql(cmd, parse_homology)

	# Retrieve non-mouse Markers w/ Accession numbers (_Species_key = 2, 40)

	cmd = '''select distinct 
	      m._Species_key, m.species, m.symbol, m.name, m.chromosome, 
	      offset = m.cytogeneticOffset, m.accID 
              from HMD_Homology h, HMD_Homology_Marker hm, MRK_NonMouse_View m
	      where h._Class_key = %s and h._Refs_key = %s
	      and h._Homology_key = hm._Homology_key
	      and hm._Marker_key = m._Marker_key order by _Species_key
	      ''' % (classKey, refKey)
	mgdlib.sql(cmd, parse_homology)

	# Retrieve non-mouse Markers w/out Accession numbers (_Species_key not in (1,2,40)

	cmd = '''select distinct 
	      m._Species_key, species = s.name + " (" + s.species + ")", m.symbol, m.name, 
	      m.chromosome, offset = m.cytogeneticOffset
              from HMD_Homology h, HMD_Homology_Marker hm, MRK_Marker m, MRK_Species s
	      where h._Class_key = %s and h._Refs_key = %s
	      and h._Homology_key = hm._Homology_key
	      and hm._Marker_key = m._Marker_key
	      and m._Species_key not in (1,2,40)
	      and m._Species_key = s._Species_key
	      order by m._Species_key
	      ''' % (classKey, refKey)
	mgdlib.sql(cmd, parse_homology)

#
# Main
#

fp = reportlib.init(sys.argv[0], 'Homology', os.environ['QCREPORTOUTPUTDIR'])
mgdlib.sql(sys.argv[1], parse_reference)
reportlib.finish_ps(fp)

