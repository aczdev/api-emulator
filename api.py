# api.py - code of API service for the Forum Staniszow page 

#!/usr/bin/env python
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_cache import Cache
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api
import crawl
import requests

fakeapi = Flask(__name__)
api = Api(fakeapi)

cors = CORS(fakeapi)

fakeapi.config['CACHE_TYPE'] = 'simple'
fakeapi.config['CORS_HEADERS'] = 'Content-Type'
cache = Cache(fakeapi, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': '/home/ubuntu/fakeapi'})

LINK = 'http://www.forumstaniszow.pl'


@fakeapi.route('/news', methods=['GET'], strict_slashes=False)
@cache.cached(timeout=60*60*6)
def headers_get():
    headers_link = LINK + '/news/all/#cale'
    return jsonify(headers = crawl.get_headers(headers_link))



@fakeapi.route('/news/active', methods=['GET'], strict_slashes=False)
@cache.cached(timeout=60*60*6)
def active_get():
    headers_link = LINK + '/news/all/#act'
    return jsonify(active = crawl.get_headers(headers_link, active=True))


@fakeapi.route('/status', methods=['GET'], strict_slashes=False)
@cross_origin()
def get_status():
    return jsonify(status = crawl.status())


@fakeapi.route('/', methods=['GET'], strict_slashes=False)
def index():
    info = {
            'author': 'ACz',
            'description': 'API emulator for an API-less page',
            'date': '06-10-2016'
        }
    return jsonify(info=info)


class News(Resource):
    def get(self, news_id):
        content_link = LINK + '/news/' + news_id + '/'
        return jsonify(news = crawl.get_content(content_link, news_id))
    
api.add_resource(News, '/news/<news_id>', strict_slashes=False)


if __name__ == '__main__':
    fakeapi.run(debug=True, port=8008, host='127.0.0.1')

