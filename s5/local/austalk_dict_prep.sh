#!/bin/bash

AUSTALKDIR=$1

[ -f $AUSTALKDIR/lexicon_samba ] || exit 1 

mkdir -p data/local/dict

./local/Prepare_dict.py $AUSTALKDIR/lexicon_samba data/local/dict/lexicon.tmp

cat data/local/dict/lexicon.tmp | sort -u > data/local/dict/lexicon.txt

cat data/local/dict/lexicon.txt | cut -d' ' -f2- | tr ' ' '\n' | sort -u > data/local/dict/nonsilence_phones.txt


echo '<UNK> SPN' >> data/local/dict/lexicon.txt

echo "SIL" > data/local/dict/optional_silence.txt

(echo SIL; echo SPN; echo NSN) > data/local/dict/silence_phones.txt


