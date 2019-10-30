#!/bin/bash

echo -e "calibration\tconversation\tinterview\tmaptask\tre-told_story\tyes-no"
for s in $1/*; do echo -ne "$(basename $s)\t"; for i in calibration  conversation  interview  maptask  re-told_story  yes-no; do [ -d $s/$i ] && echo -ne "$(find $s/$i/ -name '*.TextGrid' | wc -l)\t" || echo -ne "0\t"; done; echo ;done
