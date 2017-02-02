#!/usr/bin/python3

from collections import OrderedDict
import subprocess
import os

#"/home/juliano/resources/"
BASE_DIR = None
PARSER_EVAL = "bazel-bin/syntaxnet/parser_eval"
MODEL_DIR = "syntaxnet/models/parsey_mcparseface"


def configure(base_dir):
    global BASE_DIR
    BASE_DIR = base_dir

    global ROOT_DIR
    ROOT_DIR = os.path.join(BASE_DIR, "models/syntaxnet")


def open_parser_eval(args):
    if BASE_DIR is not None:
        return subprocess.Popen(
            [PARSER_EVAL] + args,
            cwd=ROOT_DIR,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )

def send_input(process, input):
    process.stdin.write(input.encode("utf8"))
    process.stdin.write(b"\n\n")  # signal end of documents
    process.stdin.flush()

    response = b""
    while True:
        line = process.stdout.readline()
        if line.strip() == b"":
            # empty line signals end of response
            break
        response += line
    return response.decode("utf8")

def split_tokens(parse):
    # Format the result.
    def format_token(line):
        x = OrderedDict(zip(
            ["index", "token", "unknown1", "label", "pos", "unknown2", "parent", "relation", "unknown3", "unknown4"],
            line.split("\t")
        ))
        x["index"] = int(x["index"])
        x["parent"] = int(x["parent"])
        del x["unknown1"]
        del x["unknown2"]
        del x["unknown3"]
        del x["unknown4"]
        return x

    return [
        format_token(line)
        for line in parse.strip().split("\n")
        ]

def parse_init(base_dir):
    configure(base_dir)
    pos_tagger = open_parser_eval([
        "--input=stdin",
        "--output=stdout-conll",
        "--hidden_layer_sizes=64",
        "--arg_prefix=brain_tagger",
        "--graph_builder=structured",
        "--task_context=" + MODEL_DIR + "/context.pbtxt",
        "--model_path=" + MODEL_DIR + "/tagger-params",
        "--slim_model",
        "--batch_size=1",
        "--alsologtostderr",
    ])

    # Open the syntactic dependency parser.
    dependency_parser = open_parser_eval([
        "--input=stdin-conll",
        "--output=stdout-conll",
        "--hidden_layer_sizes=512,512",
        "--arg_prefix=brain_parser",
        "--graph_builder=structured",
        "--task_context=" + MODEL_DIR + "/context.pbtxt",
        "--model_path=" + MODEL_DIR + "/parser-params",
        "--slim_model",
        "--batch_size=1",
        "--alsologtostderr",
    ])
    return pos_tagger, dependency_parser

def parse_sentence(sentence, tags, pos_tagger, dependency_parser):
    # Open the part-of-speech tagger.
    if "\n" in sentence or "\r" in sentence:
        raise ValueError()

    if sentence is not None:
    # Do POS tagging.
        pos_tags = send_input(pos_tagger, sentence + "\n")
    else:
        pos_tags = tags

    # Do syntax parsing.
    dependency_parse = send_input(dependency_parser, pos_tags)

    # Make a tree.
    dependency_parse = split_tokens(dependency_parse)
    tokens = {tok["index"]: tok for tok in dependency_parse}
    tokens[0] = OrderedDict([("sentence", sentence)])
    for tok in dependency_parse:
        tokens[tok['parent']] \
            .setdefault('tree', OrderedDict()) \
            .setdefault(tok['relation'], []) \
            .append(tok)
        del tok['parent']
        del tok['relation']

    return tokens[0]


if __name__ == "__main__":
    import sys, pprint
    pos_tagger, dependency_parser = parse_init("/opt/tensorflow")
    pprint.pprint(parse_sentence("Translate my CV from English to Portuguese", None, pos_tagger, dependency_parser))
    pprint.pprint(parse_sentence("Change my CV from English to Portuguese", None, pos_tagger, dependency_parser))
