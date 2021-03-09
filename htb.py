#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.
#
# $ pip install Flask python-dotenv requests xmljson


# Import
from collections import OrderedDict
from datetime import datetime
from json import dumps
from shutil import move
from tqdm import tqdm
from xml.etree.ElementTree import fromstring
from xmljson import BadgerFish
import math
import os
import requests
import settings


# 定数
FILE_PATH = os.path.join('.', 'result.ndjson')

USER_NAME = settings.USER_NAME
BASE_URI = 'https://b.hatena.ne.jp/' + USER_NAME + '/bookmark.rss?page='

COUNT_PER_PAGE = 20

TQDM_ENABLED = True

b = settings.b
rk = settings.rk
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:68.0) Gecko/20100101 Firefox/68.0'


# Init
yahoo = BadgerFish(dict_type=OrderedDict)


def file_exist_check():
    if os.path.exists(FILE_PATH):
        move(
            FILE_PATH,
            FILE_PATH + '.' + datetime.now().strftime('%Y%m%d%H%M%S')
        )


def write_result(content):
    with open(FILE_PATH, 'a', encoding='utf_8') as file:
        file.write(content)


def json2ndjson(parsed_text):
    parsed_text = parsed_text.replace('}, {"@about":', '}\n{"@about":')
    parsed_text = parsed_text[1:-2]
    return parsed_text


def get_rss_files():
    file_exist_check()

    uri = BASE_URI + '1'
    first_page_content = get_rss_file(uri)
    total_number = parse_rss_counts(first_page_content)
    all_page_count = math.ceil(total_number / COUNT_PER_PAGE)
    # print(total_number, all_page_count)

    if TQDM_ENABLED:
        bar = tqdm(total=all_page_count)
    parsed_text = json2ndjson(parse_rss_items(first_page_content))
    write_result(parsed_text + '\n')
    if TQDM_ENABLED:
        bar.update(1)

    for page in range(1, all_page_count):
        uri = BASE_URI + str(page + 1)
        page_content = get_rss_file(uri)
        parsed_text = json2ndjson(parse_rss_items(page_content))
        write_result(parsed_text + '\n')
        if TQDM_ENABLED:
            bar.update(1)

    if TQDM_ENABLED:
        bar.close()


def get_rss_file(uri):
    try:
        cookies = dict(b=b, rk=rk)
        headers = {'User-Agent': USER_AGENT}

        response = requests.get(uri, cookies=cookies, headers=headers)
        if response.status_code == requests.codes.ok:
            return response.text
        else:
            print(response.status_code)
            return ''
    except Exception as e:
        print(e.code, e.read())


def remove_ns(xml_content):
    return xml_content.replace(
        '<rdf:', '<').replace('</rdf:', '</').replace(' rdf:', ' ').replace(
            ' admin:', ' ').replace(
                '<content:', '<').replace('</content:', '</').replace(
                    '<dc:', '<').replace('</dc:', '</').replace(
                        '<hatena:', '<').replace('</hatena:', '</').replace(
                            ' syn:', ' ').replace(
                                '<taxo:', '<').replace('</taxo:', '</').replace(
                                    ' xmlns:', ' ').replace(
                                        'xmlns="http://purl.org/rss/1.0/"', '')


def parse_rss_counts(first_page_content):
    first_page_content = remove_ns(first_page_content)
    rss_dict = yahoo.data(fromstring(first_page_content))
    description = str(rss_dict['RDF']['channel']['description']['$'])
    TITLE_SPLIT_TEXT = 'のはてなブックマーク ('
    total_number = int(
        (description.split(TITLE_SPLIT_TEXT)[1]).replace(
            ',', '').replace(')', '')
    )

    return total_number


def parse_rss_items(xml_content):
    xml_content = remove_ns(xml_content)
    rss_dict = yahoo.data(fromstring(xml_content))
    rss_dict = rss_dict['RDF']['item']
    rss_json = dumps(rss_dict, indent=None)
    return rss_json


def main():
    get_rss_files()


if __name__ == '__main__':
    main()
