#!/usr/bin/sh

dir=$1
for file in `ls $dir | grep .py$`
do
    echo $dir/$file
    /opt/python3.7/bin/2to3 -w $dir/$file
    sed -i 's/string./str./g' $dir/$file

done
