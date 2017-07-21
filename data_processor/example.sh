#!/bin/bash

MALLET_BIN_DIR=$MALLET/bin
INPUT_FILE="../data/acl/acl.jsonlist.gz"
BACKGROUND_FILE="../data/nips/nips.jsonlist.gz"
DATA_OUPUT_DIR="acl_example/processing/"
FINAL_OUTPUT_DIR="acl_example/output/"
PREFIX="acl"

python main.py --input_file $INPUT_FILE --data_output_dir $DATA_OUPUT_DIR --final_output_dir $FINAL_OUTPUT_DIR --mallet_bin_dir $MALLET_BIN_DIR --option keywords --num_ideas 100 --prefix $PREFIX --background_file $BACKGROUND_FILE --group_by year --objects_location keywords_data.p --no_create_graphs
# python main.py --input_file $INPUT_FILE --data_output_dir $DATA_OUPUT_DIR --final_output_dir $FINAL_OUTPUT_DIR --mallet_bin_dir $MALLET_BIN_DIR --option topics --num_ideas 50 --prefix $PREFIX


# Key words take 2 minutes on all runs regardless
# Topics take ~25minutes to run on zin for the first time, and about 4 seconds for subsequent runs
