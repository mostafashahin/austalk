#!/bin/bash
#
#This code for preparing the data/l/dict dirictory of OGI kids data for kaldi ASR training
#Should be run from s5 directory


if [ $# != 1 ]; then
	echo "Usage: $(basename $0) /path/to/austalk_data"
        exit 1;
fi

#Make sure that srilm installed
echo $KALDI_ROOT/tools/srilm/bin/i686-m64
which ngram-count
if [ $? -ne 0 ]; then 
    if [ -d $KALDI_ROOT/tools/srilm/bin/i686-m64 ]; then 
        export PATH=$PATH:$KALDI_ROOT/tools/srilm/bin/i686-m64
    fi
fi


AUSTALKROOT=$1
langdir=`pwd`/data/lang
dir=`pwd`/data/local/lm_srilm

#TODO check existance of srilm, exit if not exist

#Check if dir exist, otherwise create it
[ -d $dir ] || mkdir -p $dir || exit 1

#Check if items.csv exist
[ -f $AUSTALKROOT/items.csv ] || exit 1 
#Get Text from items.csv file
cat $AUSTALKROOT/items.csv | tail -n+2 | cut -d',' -f1 | sort -u  | tr '[:lower:]' '[:upper:]' | sed 's/[;\/?!:,"-]//g' > $dir/txt.tmp
#cat $AUSTALKROOT/items.csv | cut -d',' -f1 | sort -u  | tr '[:lower:]' '[:upper:]' > $dir/txt.tmp


cat $dir/scripted.txt | tr " " "\n" | sort -u > $dir/words.tmp


#Use ngram-count from srilm to generate bi gram LM from the list of scripted words

ngram-count -text $dir/txt.tmp -order 2 -lm $dir/bi.lm

#convert to fst format

arpa2fst --disambig-symbol=#0 --read-symbol-table=$langdir/words.txt $dir/bi.lm $langdir/G.fst
