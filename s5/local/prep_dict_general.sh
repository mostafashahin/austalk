#!/bin/bash

InDict=$1
OutDir=$2

[ -f $InDict  ] || (echo "$InDict not exist" && exit 1)
[ -d $OutDir/dict  ] || mkdir -p $OutDir/dict 


./local/Prepare_dict.py $InDict $OutDir/dict/lexicon.tmp

cat $OutDir/dict/lexicon.tmp | sort -u > $OutDir/dict/lexicon.txt

cat $OutDir/dict/lexicon.txt | cut -d' ' -f2- | tr ' ' '\n' | sort -u > $OutDir/dict/nonsilence_phones.txt

echo '<UNK> SPN' >> $OutDir/dict/lexicon.txt

echo "SIL" > $OutDir/dict/optional_silence.txt

(echo SIL; echo SPN; echo NSN) > $OutDir/dict/silence_phones.txt

./utils/prepare_lang.sh $OutDir/dict "<UNK>" $OutDir/lang_tmp $OutDir/lang || exit 1
