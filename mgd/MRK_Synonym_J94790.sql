
print ""
print "Synonyms that require proper J number assignment"
print ""
print "The following synonyms associated with J:94790 (temporary J number)"
print "need to be checked individually and a proper J number and synonym type"
print "(if necessary) should be assigned.  See TR 5686."
print ""

select symbol = substring(m.symbol,1,25), synonym = substring(s.synonym,1,100)
from MRK_Marker m, MGI_Synonym s
where s._MGIType_key = 2
and s._Refs_key = 95873
and s._Object_key = m._Marker_key
order by m.symbol
go

