#!/bin/bash

txtgridScp=$1
wavscp=$2
n=$3

shuf -n $n  $txtgridScp > txtgrids

cat txtgrids | while read line; do echo $(basename $line .TextGrid) | grep -f - $wavscp | cut -d' ' -f2; done > wavlist

cat txtgrids wavlist | tar -cvzf samples.tar.gz -T -
