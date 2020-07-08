#!/bin/bash

. ./cmd.sh
. ./path.sh
set -e # exit on error

stage=0
n=15 #$(nproc)

#Call data preparation script with the path to the AusTalk data (must contains the docs disrectory)

AUSTALKROOT=/srv/scratch/z5173707/Dataset/AusTalk/
#set flags
#data_prep_opt='-r -s' #-r to activate read data, -s to activate spontaneous data

if [ $stage -le 0 ]; then
    #Prepare data: generate text, wav.scp, ...
    #local/austalk_data_prep.sh $AUSTALKROOT -x || exit 1
    
    #Generate MFCC
    
    #for part in train test dev; do
    #    mfccdir=data/$part/mfcc
    #    mfcclog=exp/make_mfcc/$part
    #    mkdir -p $mfccdir $mfcclog
    #    steps/make_mfcc.sh --nj $n --cmd "$train_cmd" data/$part $mfcclog $mfccdir
    #    steps/compute_cmvn_stats.sh data/$part $mfcclog $mfccdir
    #done
    
    #Prepare dict dirictory
    
    local/austalk_dict_prep.sh $AUSTALKROOT || exit 1  #I'm using set -e in the begining not sure if exit 1 needed
    #Prepare lang directory
    
    utils/prepare_lang.sh data/local/dict "<UNK>" data/local/lang data/lang || exit 1
    #Train bi gram LM
    echo "Train LM"
    local/austalk_train_srilm.sh $AUSTALKROOT || exit 1
fi

if [ $stage -le 1 ]; then
    
    #Train Monophone model
    steps/train_mono.sh --nj $n --cmd "$train_cmd" data/train/ data/lang/ exp/mono || exit 1
    
    #Decode the monophone model
    utils/mkgraph.sh --mono data/lang exp/mono exp/mono/graph
    steps/decode.sh --config conf/decode.config --nj $n --cmd "$decode_cmd" exp/mono/graph data/test exp/mono/decode

    # Get alignments from monophone system.
    steps/align_si.sh --nj $n --cmd "$train_cmd" data/train data/lang exp/mono exp/mono_ali

fi

if [ $stage -le 2 ]; then
    #Train Triphone Model
    steps/train_deltas.sh --cmd "$train_cmd" 1800 9000 data/train data/lang exp/mono_ali exp/tri1

    #Decode the triphone model
    utils/mkgraph.sh data/lang exp/tri1 exp/tri1/graph
    
    steps/decode.sh --config conf/decode.config --nj $n --cmd "$decode_cmd" \
    exp/tri1/graph data/test exp/tri1/decode
    
    # align tri1
    steps/align_si.sh --nj $n --cmd "$train_cmd" \
  --use-graphs true data/train data/lang exp/tri1 exp/tri1_ali
fi

if [ $stage -le 3 ]; then
    #Train tri2b [LDA+MLLT]
    steps/train_lda_mllt.sh --cmd "$train_cmd"  --splice-opts "--left-context=3 --right-context=3" 1800 9000 data/train data/lang exp/tri1_ali exp/tri2b

    #Decode the tri2b model
    utils/mkgraph.sh data/lang exp/tri2b exp/tri2b/graph
    steps/decode.sh --config conf/decode.config --nj $n --cmd "$decode_cmd" \
    exp/tri2b/graph data/test exp/tri2b/decode
    
    
    # you could run these scripts at this point, that use VTLN.
    # local/run_vtln.sh
    # local/run_vtln2.sh

    #Align tri2b
    steps/align_si.sh --nj $n --cmd "$train_cmd" --use-graphs true \
    data/train data/lang exp/tri2b exp/tri2b_ali
fi

if [ $stage = 4 ]; then
    
    #Do MMI on top of LDA+MLLT.
    steps/make_denlats.sh --nj $n --cmd "$train_cmd" \
      data/train data/lang exp/tri2b exp/tri2b_denlats
    steps/train_mmi.sh data/train data/lang exp/tri2b_ali exp/tri2b_denlats exp/tri2b_mmi
    #Decode
    steps/decode.sh --config conf/decode.config --iter 4 --nj $n --cmd "$decode_cmd" \
       exp/tri2b/graph data/test exp/tri2b_mmi/decode_it4
    steps/decode.sh --config conf/decode.config --iter 3 --nj $n --cmd "$decode_cmd" \
       exp/tri2b/graph data/test exp/tri2b_mmi/decode_it3 


    # Do the same with boosting.
    steps/train_mmi.sh --boost 0.05 data/train data/lang \
       exp/tri2b_ali exp/tri2b_denlats exp/tri2b_mmi_b0.05
    steps/decode.sh --config conf/decode.config --iter 4 --nj $n --cmd "$decode_cmd" \
       exp/tri2b/graph data/test exp/tri2b_mmi_b0.05/decode_it4
    steps/decode.sh --config conf/decode.config --iter 3 --nj $n --cmd "$decode_cmd" \
       exp/tri2b/graph data/test exp/tri2b_mmi_b0.05/decode_it3

    # Do MPE.
    steps/train_mpe.sh data/train data/lang exp/tri2b_ali exp/tri2b_denlats exp/tri2b_mpe
    steps/decode.sh --config conf/decode.config --iter 4 --nj $n --cmd "$decode_cmd" \
       exp/tri2b/graph data/test exp/tri2b_mpe/decode_it4
    steps/decode.sh --config conf/decode.config --iter 3 --nj $n --cmd "$decode_cmd" \
       exp/tri2b/graph data/test exp/tri2b_mpe/decode_it3
fi

if [ $stage -le 5 ]; then
    #Train LDA+MLLT+SAT
    steps/train_sat.sh 1800 9000 data/train data/lang exp/tri2b_ali exp/tri3b

    #Decode
    utils/mkgraph.sh data/lang exp/tri3b exp/tri3b/graph
    
    steps/decode_fmllr.sh --config conf/decode.config --nj $n --cmd "$decode_cmd" \
    exp/tri3b/graph data/test exp/tri3b/decode

    # Align all data with LDA+MLLT+SAT system (tri3b)
    steps/align_fmllr.sh --nj $n --cmd "$train_cmd" --use-graphs true \
    data/train data/lang exp/tri3b exp/tri3b_ali


    # MMI on top of tri3b (i.e. LDA+MLLT+SAT+MMI)
    steps/make_denlats.sh --config conf/decode.config \
    --nj $n --cmd "$train_cmd" --transform-dir exp/tri3b_ali \
    data/train data/lang exp/tri3b exp/tri3b_denlats
    steps/train_mmi.sh data/train data/lang exp/tri3b_ali exp/tri3b_denlats exp/tri3b_mmi

    steps/decode_fmllr.sh --config conf/decode.config --nj $n --cmd "$decode_cmd" \
    --alignment-model exp/tri3b/final.alimdl --adapt-model exp/tri3b/final.mdl \
    exp/tri3b/graph data/test exp/tri3b_mmi/decode

    # Do a decoding that uses the exp/tri3b/decode directory to get transforms from.
    steps/decode.sh --config conf/decode.config --nj $n --cmd "$decode_cmd" \
    --transform-dir exp/tri3b/decode  exp/tri3b/graph data/test exp/tri3b_mmi/decode2

fi


