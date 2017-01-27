#!/usr/bin/python3

# sudo apt-get install python3-pip
# sudo pip3 install flask

import os
import sys

from flask import Flask, request, Response
from multiprocessing import Pool
import json

import parser

base_dir = None
app = Flask(__name__)
port = 80 if os.getuid() == 0 else 8000

pool = Pool(1, maxtasksperchild=50)


@app.route('/', methods=['POST', 'GET'])
def index():
    tags = None

    if request.method == 'GET':
        sentence = request.args.get("sentence", "")
        if sentence is None:
            tags = request.args.get("tags", "")
    else:
        sentence = request.get_json()['q']
    result = pool.apply(parser.parse_sentence, [sentence, tags, base_dir])

    return Response(
        response=json.dumps(result, indent=2),
        status=200,
        content_type="application/json")


if __name__ == '__main__':
    base_dir = sys.argv[1]
    app.run(debug=False, port=port, host="0.0.0.0")
