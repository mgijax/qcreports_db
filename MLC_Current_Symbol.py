#!/usr/local/bin/python

'''
#
# MLC_Current_Symbol.py 02/19/99
#
# Report:
#       Detail information for MLC entry
#
# Usage:
#       MLC_Current_Symbol.py _Marker_key
#
#	where:
#	
# 	_Marker_key is unique identifier of symbol in MLC 
#
# Generated from:
#       Editing Interface, MLC Report form
#
# Notes:
#
# History:
#
#	lec	02/10/1999
#	- TR 322; MLC_History_edit is obsolete
#
#	lec	01/11/1999
#	- changed report name format to symbol-MMDDYYYY-MLC.rpt
#
#	lec	01/13/97
#	- added comment section
#	- replaced tostr() witih mgdlib.prvalue()
#
#	gld	01/31/96
#	- written by gld
#
'''
 
import sys
import os
import string
import mgdlib
import reportlib
import regex
import regsub

def split(str, pat, preserve = 0 ):
	# Adapted from regsub.split except that the matched patterns
	# may be preserved in the result.
	prog = regex.compile(pat)
	res = []
	start = next = 0
	while prog.search(str, next) >= 0:
		regs = prog.regs
		a, b = regs[0]
		if a == b:
			next = next + 1
			if next >= len(str):
				break
		else:
			if a > start:
				res.append(str[start:a])
			if preserve:
				res.append(str[a:b])
			start = next = b
	if len(str) > start:
		res.append(str[start:])
	return res


class TextFormatter:
	def __init__(self,txt):	
		# flag paragraphs
		self.txt = regsub.gsub('\n[\t ]+',' |==| ',txt)
		# remove CRs and whitespace after a line's text
		self.txt = regsub.gsub('[\t ]*\n',' ',self.txt)
			
		self.tl = split(self.txt,' ',1)
		self.pos = -1	# position in the text that has been output
		self.maxpos = len(self.tl)
		self.linelen = 80 # default linelen
		self.newpara = 0  #  
		self.nblanks = 3  # number of blanks to start a paragraph

	def setll(self,ll):
		self.linelen = ll

	# reset word pointer to beginning of text 
	def rewind(self):
		self.pos = 0

	# getline
	#
	# returns a line from the point the last line ended 
	# conforming to the linelength restrictions
	#
	def getline(self):
		if self.pos + 1 >= self.maxpos:
			return ''
		l, llen = [], 0   # line list and accum line length
		while len(l) == 0 and self.pos + 1 < self.maxpos:
			if self.newpara:  # then we are at the beginning of a paragraph
				l.append('\n' + self.nblanks*' ')
				self.pos = self.pos + 2 # one for '|==|', one for ' ' 
				llen = llen + self.nblanks 
				self.newpara = 0
			while self.pos + 1 < self.maxpos and  \
				llen + len(self.tl[self.pos + 1]) <= self.linelen:
				word = self.tl[self.pos + 1] # alias the word 
				if word == '|==|' or word == '\\beginpre' or \
					word == '\\endpre':  # paragraph reached, flush line
					self.newpara = 1
					break
				if word == ' ' and len(l) == 0:  # skip blanks
					self.pos = self.pos + 1  # inc word pointer
					continue	
				l.append(word)
				llen = llen + len(word)  # inc line length
				self.pos = self.pos + 1  # inc word pointer
		return string.joinfields(l,'')  # assemble the string

CRT = reportlib.CRT

mode=''
description=''
symbol=''
name=''
chrom=''
modification_date=''
userID=''
classes=[]
refs=[]

def parse_mode_description(t):
	global mode, description, modification_date, userID
	mode = t['mode']
	description = t['description']
	modification_date = t['modDate']
	userID = t['userID']

def parse_symbol_name_chr(t):
	global symbol,name,chrom,fp

	symbol = t['symbol']
	name = t['name']
	chrom = t['chromosome']

	if fp is None:
		reportName = symbol + '-' + mgdlib.date('%m%d%Y') + '-MLC'
		fp = reportlib.init(reportName, 'MLC Symbol Report', os.environ['QCREPORTOUTPUTDIR'])

def parse_classes(t):
	global classes
	classes.append(t['name'])

def parse_references(t):
	global refs
	refs.append((t['tag'],t['jnum'],t['short_citation']))

#######################################################

fp = None
mk=sys.argv[1]

cmd = 'select symbol, name, chromosome from MRK_Marker where ' + \
		'_marker_key = ' + mk
mgdlib.sql(cmd, parse_symbol_name_chr)

cmd = 'select name from MRK_Classes_View where _marker_key = ' + mk
mgdlib.sql(cmd, parse_classes)

cmd = 'select b._Refs_key, r.tag, b.jnum, b.short_citation ' + \
        'from MLC_Reference_edit r, BIB_View b ' + \
        'where r._Marker_key = ' + mk + ' and r._Refs_key = b._Refs_key ' + \
		'order by r.tag'
mgdlib.sql(cmd, parse_references)

cmd = 'select mode, description, modDate = convert(char(25), modification_date), userID ' + \
	'from MLC_Text_edit where _marker_key = ' + mk
mgdlib.sql(cmd, parse_mode_description)

indent=0 

fp.write(string.ljust('Symbol:', 10) + symbol + CRT)
fp.write(string.ljust('Chr:', 10) + mgdlib.prvalue(chrom) + CRT)
fp.write(string.ljust('Name:', 10) + mgdlib.prvalue(name) + CRT)
fp.write(string.ljust('Mode:', 10) + mgdlib.prvalue(mode) + 2*CRT)

fp.write('Classifications' + CRT)
fp.write(15*'-' + CRT)
for cl in classes:
	fp.write(indent*' ' + cl + CRT) 
fp.write(2*CRT)

fp.write('References' + CRT)
fp.write(string.ljust('#', 10) + string.ljust('jnum',10) + 'citation' + CRT)
fp.write(30*'-' + CRT)
for ref in refs:
	tag = `ref[0]`
	if len(tag) == 0:
			tag = 'NULL'
	jnum = `ref[1]`
	if len(jnum) == 0:
		jnum = 'NULL'
	citation = ref[2]
	if len(citation) == 0:
			citation = 'NULL'
	fp.write(string.ljust(tag, 10) + string.ljust(jnum,10) + citation + CRT)
fp.write(2*CRT)

fp.write('Description' + CRT)
fp.write(40*'-' + CRT)
tf = TextFormatter(description)
tf.setll(77)  # change to 77

fdesc = ''
l = tf.getline()
while l != '': 
	fdesc = fdesc + l + CRT
	l = tf.getline()
fp.write(fdesc)
fp.write(2*CRT)

fp.write('Modification date:  ' + mgdlib.prvalue(modification_date) + \
	' by user ' + mgdlib.prvalue(userID))

reportlib.finish_nonps(fp)
