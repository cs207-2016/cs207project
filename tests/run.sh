#!/bin/bash
current_dir=$(pwd)
shortName=`echo $current_dir | rev | cut -d"/" -f2-  | rev`
file_dir=$shortName'/''tsbtreedb''/''similarity.py'
#echo $file_dir
#python ../tsbtreedb/similarity.py
python $file_dir
