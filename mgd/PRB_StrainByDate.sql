
set nocount on
go

select s._Strain_key into #exclude
from PRB_Strain s
where 
(s.strain like '%/Mmcd%' and s.creation_date = '06/07/2011')
or
(s.strain like '%/Mmucd%' and s.creation_date = '09/24/2012')
or
(s._CreatedBy_key = 1421 and s.creation_date = '01/04/2013')
or
(s._CreatedBy_key = 1421 and s.creation_date = '01/09/2013')
or
(s._CreatedBy_key = 1421 and s.creation_date = '01/15/2013')
or
(s._CreatedBy_key = 1421 and s.creation_date = '02/20/2013')
or
(s._CreatedBy_key = 1421 and s.creation_date = '03/22/2013')
or
(s._CreatedBy_key = 1421 and s.creation_date = '06/10/2013')
or
(s._CreatedBy_key = 1421 and s.creation_date = '07/16/2013')
or
(s._CreatedBy_key = 1421 and s.creation_date = '08/08/2013')
or
(s._CreatedBy_key = 1421 and s.creation_date = '09/17/2013')
or
(s._CreatedBy_key = 1421 and s.creation_date = '10/08/2013')
or
(s._CreatedBy_key = 1421 and s.creation_date = '11/19/2013')
or
(s._CreatedBy_key = 1421 and s.creation_date = '12/09/2013')
or
(s._CreatedBy_key = 1421 and s.creation_date = '01/21/2014')
or
(s._CreatedBy_key = 1421 and s.creation_date = '04/09/2014')
go

create index idx1 on #exclude(_Strain_key)
go

set nocount off
go

print ''
print 'Strains - Non Standard - Sorted by Creation Date'
print '(do not include any strains flagged as needing review by Janans load)'
print ''
print 'excludes /Mmcd from 06/07/2011'
print 'excludes /Mmucd from 09/24/2012'
print 'excludes "mberry" from 01/04/2013, 01/09/2013, 01/15/2013, 02/20/2013, 03/22/2013, 06/10/2013, 07/16/2013, 08/08/2013'
print 'excludes "mberry" from 09/17/2013, 10/08/2013, 11/19/2013, 12/09/2013, 01/21/2014, 04/09/2014'
print 'excludes created-by = "strainautoload"'
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
where s._Strain_key = n._Object_key
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
where s._Strain_key = n._Object_key
and n.term = 'Needs Review - load')
and not exists (select 1 from #exclude e where s._Strain_key = e._Strain_key)
)
order by creation_date desc, strain
go

print ''
print 'Strains - Non Standard - Sorted by Creation Date'
print '(do not include any strains flagged as needing review by Janans load)'
print ''
print 'includes /Mmcd from 06/07/2011'
print 'includes /Mmucd from 09/24/2012'
print 'includes "mberry" excluded list (see above)'
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
where s._Strain_key = n._Object_key
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
where s._Strain_key = n._Object_key
and n.term = 'Needs Review - load')
and exists (select 1 from #exclude e where s._Strain_key = e._Strain_key)
)
order by creation_date desc, strain
go

