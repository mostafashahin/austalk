#!/bin/bash

echo -e "id,comp,file,duration"
for s in $1/*; do for i in words sentences story digits; do [ -d $s/$i ] && find $s/$i/ -name '*.wav' | while read f; do echo -ne "$(basename $s),";  echo -ne "$i,"; echo -ne "$(basename $f),"; echo -e "$(soxi -D $f)" ;done ; done; done
