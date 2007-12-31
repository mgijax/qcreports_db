
print ""
print "EST IDs and Gm Markers as Synonyms"
print ""

select m.symbol, synonym = substring(s.synonym, 1, 75)
from MRK_Marker m, MGI_Synonym s, MGI_SynonymType st
where m._Marker_key = s._Object_key
and s._SynonymType_key = st._SynonymType_key
and st.synonymType = "exact"
and (s.synonym like "[A-Z][A-Z][0-9][0-9][0-9][0-9][0-9][0-9]" or s.synonym like "Gm%")
and s.synonym not like "EG%"
order by m.symbol
go

