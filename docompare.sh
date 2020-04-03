#!/usr/bin/sh

countfilename=filecounts.txt
dirpy3=$1
dirpy2=$2
outdir=$3
echo $dirpy3
echo $dirpy2
echo $outdir

totalCt=0
errorCt=0
countfile="$outdir/$countfilename"
echo $countfile
rm $countfile
touch $countfile

for file in `ls $dirpy3`
do
    totalCt=`expr $totalCt + 1`
    echo "$dirpy3/$file"
    if [ -f $dirpy3/$file ]
    then
        echo "processing $file"
        diff $dirpy3/$file $dirpy2/$file >& $outdir/$file

        ct3=`cat $dirpy3/$file | wc -l`

        ct2=`cat $dirpy2/$file | wc -l`

        if [ $ct3 -ne $ct2 ]
        then
            errorCt=`expr $errorCt + 1`
            echo ""  >> $countfile  2>&1 
            echo "python3 $file : $ct3"  >> $countfile  2>&1
            echo "python2 $file : $ct2"  >> $countfile  2>&1
            echo ""  >> $countfile  2>&1
        else
            echo $file >> $countfile  2>&1
        fi
    fi
done
echo "Total: $totalCt"  >> $countfile  2>&1
echo "Different Counts: $errorCt"  >> $countfile  2>&1
