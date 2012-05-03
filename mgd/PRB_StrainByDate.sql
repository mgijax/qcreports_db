
set nocount on
go

select s._Strain_key into #exclude
from PRB_Strain s
where s.strain like '%/Mmcd%'
and s.creation_date between '06/07/2011' and dateadd(day,1,'06/07/2011')
go

create index idx1 on #exclude(_Strain_key)
go

set nocount off
go

print ''
print 'Strains - Non Standard - Sorted by Creation Date'
print '(do not include any strains flagged as needing review by Janan''s load)'
print''
print 'excludes /Mmcd from 06/07/2011'
print 'excludes created-by = ''strainautoload'''
print ''

(
select null as jr, substring(t.term,1,30) as strainattribute, 
substring(s.strain,1,125) as strain, s.creation_date
from PRB_Strain s
     LEFT OUTER JOIN PRB_Strain_Attribute_View t on (s._Strain_key = t._Strain_key)
where s.standard = 0
and s._CreatedBy_key != 1521
and not exists (select 1 from ACC_Accession a
where a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key = 22)
and not exists (select 1 from PRB_Strain_NeedsReview_View n
where s._Strain_key = n._Strain_key
and n.term = 'Needs Review - load')
and not exists (select 1 from #exclude e where s._Strain_key = e._Strain_key)
union
select a.accID as jr, substring(t.term,1,30) as strainattribute, 
substring(s.strain,1,125) as strain, s.creation_date
from PRB_Strain s
     LEFT OUTER JOIN PRB_Strain_Attribute_View t on (s._Strain_key = t._Strain_key),
     ACC_Accession a
where s.standard = 0
and s._CreatedBy_key != 1521
and a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key = 22
and not exists (select 1 from PRB_Strain_NeedsReview_View n
where s._Strain_key = n._Strain_key
and n.term = 'Needs Review - load')
and not exists (select 1 from #exclude e where s._Strain_key = e._Strain_key)
)
order by s.creation_date desc, s.strain
go

print ''
print 'Strains - Non Standard - Sorted by Creation Date'
print '(do not include any strains flagged as needing review by Janan''s load)'
print ''
print 'includes /Mmcd from 06/07/2011'
print ''

(
select null as jr, substring(t.term,1,30) as strainattribute, 
substring(s.strain,1,125) as strain, s.creation_date
from PRB_Strain s
     LEFT OUTER JOIN PRB_Strain_Attribute_View t on (s._Strain_key = t._Strain_key)
where s.standard = 0
and s._CreatedBy_key != 1521
and not exists (select 1 from ACC_Accession a
where a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key = 22)
and not exists (select 1 from PRB_Strain_NeedsReview_View n
where s._Strain_key = n._Strain_key
and n.term = 'Needs Review - load')
and exists (select 1 from #exclude e where s._Strain_key = e._Strain_key)
union
select a.accID as jr, substring(t.term,1,30) as strainattribute, 
substring(s.strain,1,125) as strain, s.creation_date
from PRB_Strain s
     LEFT OUTER JOIN PRB_Strain_Attribute_View t on (s._Strain_key = t._Strain_key),
     ACC_Accession a
where s.standard = 0
and s._CreatedBy_key != 1521
and a._Object_key = s._Strain_key
and a._MGIType_key = 10
and a._LogicalDB_key = 22
and not exists (select 1 from PRB_Strain_NeedsReview_View n
where s._Strain_key = n._Strain_key
and n.term = 'Needs Review - load')
and exists (select 1 from #exclude e where s._Strain_key = e._Strain_key)
)
order by s.creation_date desc, s.strain
go

drop table #exclude
go

