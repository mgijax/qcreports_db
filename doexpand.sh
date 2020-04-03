#!/usr/bin/sh

dir=$1
for file in `ls $dir | grep .py$`
do
    echo $file
    expand -i $dir/$file > "$dir/$file.new"
    mv  $dir/$file "$dir/$file.bak"
    mv "$dir/$file.new" $dir/$file

    # remove python statement at top
    echo "$(tail -n +2  $dir/$file)" >  "$dir/$file"
done
