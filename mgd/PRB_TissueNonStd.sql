print ""
print "Tissues - Non Standard"
print ""

select tissue from PRB_Tissue
where standard = 0
order by tissue
go

