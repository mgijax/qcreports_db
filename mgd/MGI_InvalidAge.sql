select age = "Not Specified", ageMin = -1.0, ageMax = -1.0
into #ageLookup
union
select age = "Not Applicable", ageMin = -1.0, ageMax = -1.0
union
select age = "Not Resolved", ageMin = -1.0, ageMax = -1.0
union
select age = "embryonic", ageMin = 0.0, ageMax = 21.0
union
select age = "perinatal", ageMin = 17.0, ageMax = 22.0
union
select age = "postnatal", ageMin = 21.01, ageMax = 1846.0
union
select age = "postnatal newborn", ageMin = 21.01, ageMax = 25.0
union
select age = "postnatal immature", ageMin = 25.01, ageMax = 42.0
union
select age = "postnatal adult", ageMin = 42.01, ageMax = 1846.0
go

print ""
print "Invalid Age Min/Max"
print ""

select "GXD_Expression", e._Expression_key, age = substring(e.age,1,20), e.ageMin, e.ageMax, a.ageMin, a.ageMax
from #ageLookup a, GXD_Expression e
where a.age = e.age
and a.ageMin != e.ageMin
and a.ageMax != e.agemax
union
select "GXD_GelLane", e._GelLane_key, age = substring(e.age,1,20), e.ageMin, e.ageMax, a.ageMin, a.ageMax
from #ageLookup a, GXD_GelLane e
where a.age = e.age
and a.ageMin != e.ageMin
and a.ageMax != e.agemax
union
select "GXD_Specimen", e._Specimen_key, age = substring(e.age,1,20), e.ageMin, e.ageMax, a.ageMin, a.ageMax
from #ageLookup a, GXD_Specimen e
where a.age = e.age
and a.ageMin != e.ageMin
and a.ageMax != e.agemax
union
select "PRB_Source", e._Source_key, age = substring(e.age,1,20), e.ageMin, e.ageMax, a.ageMin, a.ageMax
from #ageLookup a, PRB_Source e
where a.age = e.age
and a.ageMin != e.ageMin
and a.ageMax != e.agemax
order by age

go

