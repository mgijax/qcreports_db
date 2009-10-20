#!/bin/sh

#
# Script for running the GO Statistics/TR 2212
#
# first, in a csh, source the Configuration file
# then, run this script
#
# 10/20/2009	lec
#	- TR 9894/add a GOA annotation check: setCreatedByClause, GOA_CLAUSE
#	this report can/should probably be moved to a python report
#

ARCHIVE_DIR=$QCARCHIVEDIR/go

#SWISS_PROT="'J:60000'"
#INTERPRO="'J:72247'"
#ORTHOLOGY="'J:73065'"
#EC="'J:72245'"
#ROOT="J:73796"

SWISS_PROT=61933
INTERPRO=73199
ORTHOLOGY=74017
EC=73197
ROOT=74750

MANUAL_NOT_IN_CLAUSE="($SWISS_PROT,$INTERPRO,$EC)"

# select created_by/login that begin with "GOA_"
GOA_CLAUSE="'GOA_%'"

COUNT_ALL_ANNOTATIONS="a._Annot_key"
COUNT_DISTINCT_MARKERS="distinct(a._Object_key)"

COUNT_ALL_REFERENCES="ALL_REFERENCES"
NOT_IN="not in"
EQUALS="="

REPORT=$QCOUTPUTDIR/GO_stats.rpt

setRefsClause()
{
   if test "$1" != "$COUNT_ALL_REFERENCES"
   then
      REFS_CLAUSE="and e._Refs_key $1 $2"
   else
      REFS_CLAUSE=""
   fi
}

setCreatedByClause()
{
   if test "$1" != ""
   then
      CREATEDBY_CLAUSE="and u.login like $1"
   else
      CREATEDBY_CLAUSE=""
   fi
}

getAnnotations()
{
   setRefsClause "$2" $3
   setCreatedByClause $4
   
isql -S${MGD_DBSERVER} -U${MGI_PUBLICUSER} -P${MGI_PUBLICPASSWORD} -w200 << END >> $REPORT

use ${MGD_DBNAME}
go

set nocount on

declare @annotations int

select @annotations = count($1)
from VOC_Annot a, VOC_Evidence e, MGI_User u
where a._AnnotType_key  = 1000
and a._Annot_key = e._Annot_key                                     
$REFS_CLAUSE
and e._CreatedBy_key = u._User_key
$CREATEDBY_CLAUSE

if "$1" = "$COUNT_DISTINCT_MARKERS"
   print "Total Number of Genes Annotated to:    %1!", @annotations
else
   print "Total Number of Annotations:    %1!", @annotations
go
END
}

getAnnotationByOntology()
{

   setRefsClause "$2" $3
   
isql -S${MGD_DBSERVER} -U${MGI_PUBLICUSER} -P${MGI_PUBLICPASSWORD} -w200 << END >> $REPORT

use ${MGD_DBNAME}
go

set nocount on
go
--Total Number of Annotations
   -- Process
   -- Function
   -- Component

declare aliascursor cursor for
select d.name, convert (char(6), count($1))
from VOC_Annot a, VOC_Evidence e, DAG_Node n, DAG_DAG d, MGI_User u
where a._AnnotType_key = 1000
and a._Annot_key = e._Annot_key
$REFS_CLAUSE
and e._CreatedBy_key = u._User_key
$CREATEDBY_CLAUSE
and a._Term_key = n._Object_key
and d._DAG_Key = n._DAG_Key
group by d.name
go

declare @ontologyName    char(30)
declare @genesAnnotated  char(30)

print "Breakdown by OntologyName:"

open  aliascursor 
fetch aliascursor into @ontologyName, @genesAnnotated
while ( @@sqlstatus = 0 )
begin 
   print "     %1!     %2!", @ontologyName, @genesAnnotated
   fetch aliascursor into @ontologyName, @genesAnnotated
end

close aliascursor
deallocate cursor aliascursor
go

END
}

getSummary1()
{

echo ""                                                                      >> $REPORT
echo "*********************************************************************" >> $REPORT
echo "GO Ontology Summary - Number of GO Terms per Ontology"                 >> $REPORT
echo ""                                                                      >> $REPORT

isql -S${MGD_DBSERVER} -U${MGI_PUBLICUSER} -P${MGI_PUBLICPASSWORD} -w200 << END >> $REPORT

use ${MGD_DBNAME}
go

set nocount on
go

select substring(d.name,1,30) "ontology", count(n._Object_key) "number of terms"
from DAG_DAG d, DAG_Node n
where d._DAG_key in (1,2,3)
and d._DAG_key = n._DAG_key
group by d._DAG_key
go

set nocount off
go

END

echo ""                                                                      >> $REPORT
echo "*********************************************************************" >> $REPORT

}

getSummary2()
{

echo "*********************************************************************" >> $REPORT
echo "GO Ontology Summary - Number of GO Terms per Ontology Used in MGI"     >> $REPORT
echo ""                                                                      >> $REPORT

isql -S${MGD_DBSERVER} -U${MGI_PUBLICUSER} -P${MGI_PUBLICPASSWORD} -w200 << END >> $REPORT

use ${MGD_DBNAME}
go

set nocount on
go

select substring(d.name,1,30) "ontology", count(n._Object_key) "number of terms"
from DAG_DAG d, DAG_Node n
where d._DAG_key in (1,2,3)
and d._DAG_key = n._DAG_key
and exists (select 1 from VOC_Annot a where n._Object_key = a._Term_key)
group by d._DAG_key
go

set nocount off
go

END

echo ""                                                                      >> $REPORT
echo "*********************************************************************" >> $REPORT

}

getCounts()
{
   echo "*********************************************************************" >> $REPORT
   echo "Processing $1 Annotations..."                                                     
   echo "$1 Annotations:"                                                       >> $REPORT
   echo "======================"                                                >> $REPORT
   getAnnotations           $COUNT_DISTINCT_MARKERS "$2" $3 $4
   getAnnotationByOntology  $COUNT_DISTINCT_MARKERS "$2" $3 $4
   echo "---------------------------------------------------------------------" >> $REPORT
   getAnnotations           $COUNT_ALL_ANNOTATIONS  "$2" $3 $4
   getAnnotationByOntology  $COUNT_ALL_ANNOTATIONS  "$2" $3 $4
   echo "*********************************************************************" >> $REPORT
}

echo "GO Stats Being Generated..."

rm -f $REPORT
${MGI_DBUTILS}/text/header.sh ${REPORT} ${MGD_DBSERVER} ${MGD_DBNAME}

getSummary1
getSummary2
getCounts "ALL"        $COUNT_ALL_REFERENCES "" ""
getCounts "HAND"        "$NOT_IN"             $MANUAL_NOT_IN_CLAUSE ""
getCounts "GOA"         "$NOT_IN"             $MANUAL_NOT_IN_CLAUSE "$GOA_CLAUSE"
getCounts "SWISS_PROT" $EQUALS               $SWISS_PROT ""
getCounts "INTERPRO"   $EQUALS               $INTERPRO ""
getCounts "ORTHOLOGY"  $EQUALS               $ORTHOLOGY ""
getCounts "EC"         $EQUALS               $EC ""
getCounts "ROOT"       $EQUALS               $ROOT ""

#Archive the file
if [ ! -d $ARCHIVE_DIR ]
then
   echo "...creating data directory $1"
   mkdir $ARCHIVE_DIR
fi
ARCHIVE_FILE_NAME="$ARCHIVE_DIR/GO_stats.`date +%Y%m%d`"
cp -p $REPORT $ARCHIVE_FILE_NAME
