print ""
print "Molecular Segments - All Standard Tissues"
print ""

select tissue from PRB_Tissue
where standard = 1
order by tissue
go

