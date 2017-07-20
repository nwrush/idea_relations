# Nikko Rush
# 7/19/17

import os
import os.path
import subprocess

is_windows = os.name == 'nt'


def run_mallet(bin_dir, directory, topics):
    cwd = directory

    mallet = os.path.join(bin_dir, "mallet")

    mallet_import_path = os.path.join(directory, "data.input")
    mallet_file = os.path.join(directory, "data.mallet")

    output_state = os.path.join(directory, "topic-state.gz")
    output_doc_topics = os.path.join(directory, "doc-topics.gz")
    output_topic_keys = os.path.join(directory, "topic-words.gz")

    # Run mallet input
    args = [mallet, "import-file", "--input", mallet_import_path, "--output", mallet_file, "--keep-sequence", "--token-regex", "'\\w+'"]
    result = subprocess.run(args, cwd=cwd)

    print(result.returncode)

    # Run mallet train-topics
    args = [mallet, "train-topics", "--input", mallet_file, "--num-topics", topics, "--output-state", output_state,
            "--output-doc-topics", output_doc_topics, "--output-topic-keys", output_topic_keys, "--num-top-words", '500']
    result = subprocess.run(args, cwd=cwd)

    print(result.returncode)
