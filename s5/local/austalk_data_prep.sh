#!/bin/bash
#
#This code for preparing the OGI kids data for kaldi ASR training
#Should be run from s5 directory

set -e

#if [ $# != 1 ]; then
#	echo "Usage: ogi_data_prep.sh /path/to/ogi_data"
#	exit 1;
#fi

export LC_ALL=C #To make sure that the sorting of files will be performed in the same way as C++

AUSTALKROOT=$1
data_prep_opt=${@:2}
comp="sentences,sentences-e,story,words-1,words-1-2,words-2,words-2-2,words-3,words-3-2"
age='0-100' #The selected grad range of children

nTrainSpkrs=694
nTestSpkrs=78
nDevSpkrs=78

trndir=data/train
tstdir=data/test
devdir=data/dev

mkdir -p $trndir $tstdir $devdir

. ./path.sh || exit 1; # for KALDI_ROOT


#Split speakers among test dev train in 3 sep files each contain list of speakers
#Write code in the shell to generate 3 dir data/train data/test data/dev and modify the below code to accept list of spekers 

touch $trndir/spkrs $tstdir/spkrs $devdir/spkrs

#Split speakers to train, test and dev by default 15% for test, 15% dev and 70% training
#Can be modified by passing optional --train_portion float, --test_portion float, --dev_portion float to the command

[ -f local/train_spkrs ] && [ -f local/test_spkrs ] && [ -f local/dev_spkrs ] || (echo "speaker split files not exists!" && exit 1) 

head -n $nTrainSpkrs local/train_spkrs > $trndir/spkrs
head -n $nTestSpkrs  local/test_spkrs > $tstdir/spkrs
head -n $nDevSpkrs local/dev_spkrs > $devdir/spkrs


for dir in  $trndir $tstdir $devdir; do
    
    local/gen_text_utt2spkr.py $AUSTALKROOT $dir/text $dir/utt2spk $dir/wav.scp -l $dir/spkrs -c $comp -a $age $data_prep_opt 

done

for dir in $trndir $tstdir $devdir; do
    #Sort Files
    sort -o $dir/text $dir/text
    sort -o $dir/utt2spk $dir/utt2spk
    sort -o $dir/wav.scp $dir/wav.scp

    utils/utt2spk_to_spk2utt.pl $dir/utt2spk > $dir/spk2utt

done
