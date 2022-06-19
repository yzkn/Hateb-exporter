#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.
#
# $ pip install Flask python-dotenv requests xmljson


# Import
from flask import Flask, Response
import htb
import math
import re
import time

import os


# Init
app = Flask(__name__)


@app.route('/')
def index():
    return '<a href="http://127.0.0.1:5000/me">http://127.0.0.1:5000/me</a>'


def generate():
    uri = htb.BASE_URI + '1'
    first_page_content = htb.get_rss_file(uri)
    total_number = htb.parse_rss_counts(first_page_content)
    all_page_count = math.ceil(total_number / htb.COUNT_PER_PAGE)

    parsed_text = htb.json2ndjson(
        htb.parse_rss_items(first_page_content))
    yield (parsed_text + '\n')

    for page in range(1, all_page_count):
        uri = htb.BASE_URI + str(page + 1)
        page_content = htb.get_rss_file(uri)
        parsed_text = htb.json2ndjson(
            htb.parse_rss_items(page_content))
        yield (parsed_text + '\n')


def generate2(start, stop):
    for page in range(int(start), int(stop)):
        uri = htb.BASE_URI + str(page)
        page_content = htb.get_rss_file(uri)
        parsed_text = htb.json2ndjson(
            htb.parse_rss_items(page_content))
        with open('output.ndjson', 'a') as file:
            file.write(parsed_text)
        yield (parsed_text + '\n')


@app.route('/user/<name>')
def user(name=None):
    # [A-Za-z0-9\-\_]

    p = re.compile('[A-Za-z0-9\-\_]{3,32}')
    if p.fullmatch(name):
        htb.BASE_URI = 'https://b.hatena.ne.jp/' + name + '/bookmark.rss?page='
        # return name

        return Response(generate(), mimetype='text/plain')
    return 'hoge'


@app.route('/me')
def generate_large_data():
    return Response(generate(), mimetype='text/plain')


@app.route('/me/<start>/<stop>')
def generate_large_data2(start, stop):
    return Response(generate2(start, stop), mimetype='text/plain')


if __name__ == "__main__":
    app.run(debug=True)
