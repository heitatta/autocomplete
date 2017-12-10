#!/usr/bin/env python

import os

from flask import Flask, jsonify, request, send_from_directory
from google.cloud import datastore

app = Flask(__name__, static_folder='static')

@app.route('/api/v1/autocomplete')
def autocomplete():
    key = request.args.get('term', '').upper()
    if key == '':
        return jsonify({})

    ds = datastore.Client()
    query = ds.query(kind="products")
    query.add_filter('key', '>=', key)
    query.add_filter('key', '<=', key + 'ZZZZZZZZZZZZZZ')
    results = []
    for row in query.fetch():
        name = row.get('name')
        results.append({'id': name, 'value': name, 'label': name})

    return jsonify(results)

@app.route('/<path:filename>')
def static_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
