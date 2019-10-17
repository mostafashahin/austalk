cat sentence2phonemes.csv2 | cut -d',' -f2 | tr ' ' '\n' > words
cat story2phonemes.csv2 | cut -d',' -f2 | tr ' ' '\n' >> words
cat sentence2phonemes.csv2 | cut -d',' -f3 | tr ' ' '\n' > trans
cat story2phonemes.csv2 | cut -d',' -f3 | tr ' ' '\n' >> trans
paste words trans > lexicon
cat words2phonemes >> lexicon
dos2unix lexicon
python3 Prepare_dict.py lexicon lexicon2
