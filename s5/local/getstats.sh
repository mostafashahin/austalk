#!/bin/bash

echo -e "id\twords\tsentences\tstory\tdigits"
for s in $1/*; do echo -ne "$(basename $s)\t"; for i in words sentences story digits; do [ -d $s/$i ] && echo -ne "$(find $s/$i/ -name '*.TextGrid' | wc -l)\t" || echo -ne "0\t"; done; echo ;done
