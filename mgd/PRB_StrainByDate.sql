print ""
print "Strains - Non Standard - Sorted by Creation Date"
print "(do not include any strains flagged as needing review by Janan's load)"
print ""

select jr = null, substring(t.term,1,30) "strainattribute", substring(s.strain,1,125) "strain", s.creation_date
from PRB_Strain s, PRB_Strain_Attribute_View t
where s.standard = 0
and s._Strain_key *= t._Strain_key
and not exists (select 1 from ACC_Accession a
where a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key = 22)
and not exists (select 1 from PRB_Strain_NeedsReview_View n
where s._Strain_key = n._Strain_key
and n.term = "Needs Review - load")
union
select jr = a.accID, substring(t.term,1,30) "strainattribute", substring(s.strain,1,125) "strain", s.creation_date
from PRB_Strain s, PRB_Strain_Attribute_View t, ACC_Accession a
where s.standard = 0
and s._Strain_key *= t._Strain_key
and a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key = 22
and not exists (select 1 from PRB_Strain_NeedsReview_View n
where s._Strain_key = n._Strain_key
and n.term = "Needs Review - load")
order by s.creation_date desc, s.strain
go

