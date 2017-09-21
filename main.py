# -*- coding: utf-8 -*-

import argparse
import datetime
import functools
import logging
import os
import pickle
import sys

import dateutil.parser

import fighting_lexicon as fl
import idea_relations as il
import mallet_topics as mt
import output_analyzer
import preprocessing

is_windows = os.name == 'nt'

logging.basicConfig(level=logging.INFO)

STEPS = 4


def parse_arguments(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--option", type=str, choices=["topics", "keywords"],
                        help=("choose using topics or keywords to represent ideas,"
                              " mallet_bin_dir is required if topic is chosen,"
                              " background_file is required if keywords is chosen."),
                        default="topics")
    parser.add_argument("--input_file",
                        help=("input file, each line is a json object "
                              "with fulldate and text"),
                        type=str)
    parser.add_argument("--data_output_dir",
                        help=("output directory for intermedia data"),
                        type=str)
    parser.add_argument("--final_output_dir",
                        help=("output directory for final results"),
                        type=str)
    parser.add_argument("--mallet_bin_dir",
                        help=("directory with Mallet binaries"),
                        type=str)
    parser.add_argument("--background_file",
                        help=("background file to learn important keywords"),
                        type=str)
    parser.add_argument("--group_by",
                        help=("binning option for timesteps, supports year, quarter, and month"),
                        type=str,
                        default="year")
    parser.add_argument("--prefix",
                        help=("name for the exploration"),
                        type=str,
                        default="exp")
    parser.add_argument("--num_ideas",
                        help=("number of ideas, i.e., "
                              "number of topics or keywords"),
                        type=int,
                        default=50)
    parser.add_argument("--tokenize",
                        help=("whether to tokenize"),
                        action="store_true")
    parser.add_argument("--lemmatize",
                        help=("whether to lemmatize"),
                        action="store_true")
    parser.add_argument("--nostopwords",
                        help=("whether to filter stopwords"),
                        action="store_true")

    parser.add_argument("--objects_location",
                        help=("File name to store graph data in."
                              "If not given, no data will be stored"),
                        type=str,
                        default=None)
    parser.add_argument("--no_create_graphs",
                        help=("whether to create graphs of relations"),
                        action="store_true")
    parser.add_argument("--force_create_topics",
                        help=("force the parser to recreate topic information instead of relying on existing files"),
                        action="store_true")
    parser.add_argument("--start_time",
                        help=("Only consider documents from after this point in time"),
                        type=str,
                        default=datetime.MINYEAR)
    parser.add_argument("--end_time",
                        help=("Only consider documents from before this point in time"),
                        type=str,
                        default=datetime.MAXYEAR)

    return parser.parse_args(args=args)


def main(args=None, parse_args=True):
    args = parse_arguments(args)

    is_subprocess = args.objects_location is not None
    if is_subprocess: print("Status:%d" % STEPS)

    input_file = os.path.abspath(args.input_file)
    data_output_dir = os.path.abspath(args.data_output_dir)
    final_output_dir = os.path.abspath(args.final_output_dir)
    if not os.path.exists(data_output_dir):
        os.makedirs(data_output_dir)
    if not os.path.exists(final_output_dir):
        os.makedirs(final_output_dir)
    # Support some standard preprocessing
    if args.tokenize:
        # tokenize input_file to token_file
        logging.info("tokenizing data")
        token_file = "%s/tokens.jsonlist.gz" % data_output_dir
        func = functools.partial(preprocessing.tokenize,
                                 filter_stopwords=args.nostopwords)
        preprocessing.preprocess_input(input_file, token_file)
        input_file = token_file

    # status message
    if is_subprocess: print("Status:1")

    if args.lemmatize:
        # lemmatize input_file to lemma_file
        logging.info("lemmatizing data")
        lemma_file = "%s/lemmas.jsonlist.gz" % data_output_dir
        func = functools.partial(preprocessing.lemmatize,
                                 filter_stopwords=args.nostopwords)
        preprocessing.preprocess_input(input_file, lemma_file)
        input_file = lemma_file

    # status message
    if is_subprocess: print("Status:2")

    # generate topics or lexicons
    option = args.option
    num_ideas = args.num_ideas
    cooccur_func = functools.partial(il.generate_cooccurrence_from_int_set,
                                     num_ideas=num_ideas)
    prefix = args.prefix
    if option == "topics":
        logging.info("using topics to represent ideas")
        prefix = "%s_topics" % prefix

        # generate mallet topics
        if args.force_create_topics or not mt.check_mallet_directory(data_output_dir):
            mt.get_mallet_input_from_words(input_file, data_output_dir)
            # run mallet to prepare topics inputs
            # users can also generate mallet-style topic inputs inputs
            logging.info("running mallet to get topics")
            if not os.path.exists(os.path.join(args.mallet_bin_dir, 'mallet')):
                sys.exit("Error: Unable to find mallet at %s" % args.mallet_bin_dir)
            if is_windows:
                rtn_code = os.system(".\mallet.bat %s %s %d" % (args.mallet_bin_dir, data_output_dir, num_ideas))
            else:
                os.system("./mallet.sh %s %s %d" % (args.mallet_bin_dir,
                                                    data_output_dir,
                                                    num_ideas))
        # load mallet outputs
        articles, vocab, idea_names = mt.load_articles(input_file, data_output_dir)
        table_top = 5
    elif option == "keywords":
        logging.info("using keywords to represent ideas")
        prefix = "%s_keywords" % prefix
        # idenfity keyword ideas using fighting lexicon
        lexicon_file = "%s/fighting_lexicon.txt" % data_output_dir
        other_files = [args.background_file]
        fl.get_top_distinguishing(input_file, other_files, data_output_dir,
                                  lexicon_file)
        # load keywords
        articles, word_set, idea_names = fl.load_word_articles(input_file,
                                                               lexicon_file,
                                                               data_output_dir,
                                                               vocab_size=num_ideas)
        table_top = 10
    else:
        logging.error("unsupported idea representations")

    if is_subprocess: print("Status:3")

    if is_subprocess:
        # Output for the visualizer
        default_time = datetime.datetime(1, 1, 1)

        start = dateutil.parser.parse(str(args.start_time), default=default_time)
        end = dateutil.parser.parse(str(args.end_time), default=default_time)

        data = output_analyzer.get_output(args, articles, idea_names, cooccur_func, name=args.prefix,
                                          group_by=args.group_by, start_time=start, end_time=end)
        # Output data is a tuple of the form: (pmi, ts_correlation, ts_matrix, idea_names)
        pickle.dump(data, open(args.objects_location, 'wb'))

        print("Status:4")

    if not args.no_create_graphs:
        logging.info("Creating graphs")
        # compute strength between pairs and generate outputs
        il.generate_all_outputs(articles, num_ideas, idea_names, prefix,
                                final_output_dir, cooccur_func,
                                table_top=table_top, group_by=args.group_by)
    return args


if __name__ == "__main__":
    main()
