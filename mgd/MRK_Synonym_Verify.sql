
print ""
print "Synonyms that need to be verified"
print ""
print "The following synonyms associated with J:66660 and J:66661"
print "(used previously to enter human ortholog synonyms)"
print "need to be checked individually and a proper J number"
print "and synonym type (if necessary) should be assigned."
print "We no longer use the above two J numbers.  See TR 5686."
print ""

select symbol = substring(m.symbol,1,25), synonym = substring(s.synonym,1,60), jnum = a.accID
from MRK_Marker m, MGI_Synonym s, ACC_Accession a
where s._MGIType_key = 2
and s._Refs_key in (67607, 67608)
and s._Object_key = m._Marker_key
and s._Refs_key = a._Object_key
and a._LogicalDB_key = 1
and a.prefixPart = "J:"
order by m.symbol
go

