#!/bin/bash

. ./cmd.sh
set -e
stage=1
generate_alignments=true
speed_perturb=true
num_jobs=20
. ./path.sh
. ./utils/parse_options.sh

train_set=train


if $speed_perturb; then
  if [ $stage -le 1 ]; then
    # Although the nnet will be trained by high resolution data, we still have
    # to perturb the normal data to get the alignments _sp stands for
    # speed-perturbed
    echo "$0: preparing directory for speed-perturbed data"
    utils/data/perturb_data_dir_speed_3way.sh --always-include-prefix true \
           data/${train_set} data/${train_set}_sp

    echo "$0: creating MFCC features for low-resolution speed-perturbed data"
    mfccdir=mfcc_perturbed
    steps/make_mfcc.sh --cmd "$train_cmd" --nj $num_jobs \
                       data/${train_set}_sp exp/make_mfcc/${train_set}_sp $mfccdir
    steps/compute_cmvn_stats.sh data/${train_set}_sp exp/make_mfcc/${train_set}_sp $mfccdir
    utils/fix_data_dir.sh data/${train_set}_sp
  fi

  if [ $stage -le 2 ] && $generate_alignments; then
    # obtain the alignment of the perturbed data
    steps/align_fmllr.sh --nj $num_jobs --cmd "$train_cmd" \
      data/${train_set}_sp data/lang exp/tri4 exp/tri4_ali_nodup_sp
  fi
  train_set=${train_set}_sp
fi
if [ $stage -le 3 ]; then
  mfccdir=mfcc_hires

  # the 100k_nodup directory is copied seperately, as
  # we want to use exp/tri2_ali_100k_nodup for lda_mllt training
  # the main train directory might be speed_perturbed
  for dataset in $train_set ; do
    utils/copy_data_dir.sh data/$dataset data/${dataset}_hires

    utils/data/perturb_data_dir_volume.sh data/${dataset}_hires

    steps/make_mfcc.sh --nj $num_jobs --mfcc-config conf/mfcc_hires.conf \
        --cmd "$train_cmd" data/${dataset}_hires exp/make_hires/$dataset $mfccdir;
    steps/compute_cmvn_stats.sh data/${dataset}_hires exp/make_hires/${dataset} $mfccdir;

    # Remove the small number of utterances that couldn't be extracted for some
    # reason (e.g. too short; no such file).
    utils/fix_data_dir.sh data/${dataset}_hires;
  done

  for dataset in dev test ; do
    # Create MFCCs for the eval set
    utils/copy_data_dir.sh data/$dataset data/${dataset}_hires
    steps/make_mfcc.sh --cmd "$train_cmd" --nj $num_jobs --mfcc-config conf/mfcc_hires.conf \
        data/${dataset}_hires exp/make_hires/$dataset $mfccdir;
    steps/compute_cmvn_stats.sh data/${dataset}_hires exp/make_hires/$dataset $mfccdir;
    utils/fix_data_dir.sh data/${dataset}_hires  # remove segments with problems
  done
fi
