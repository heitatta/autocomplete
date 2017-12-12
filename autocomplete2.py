#!/usr/bin/env python

import os

from flask import Flask, jsonify, request, send_from_directory
from google.cloud import datastore

app = Flask(__name__, static_folder='static')
os.environ['FLASK_DEBUG'] = "1"

@app.route('/api/v1/autocomplete')
def autocomplete():
    key = request.args.get('term', '').upper()
    if key == '':
        return jsonify({})

    ds = datastore.Client()
    query = ds.query(kind="products2")
    query.add_filter('key', '=', key)
    query.order = ['-bestSellingRank']
    results = []
    for row in query.fetch(limit=50):
        name = row.get('name')
        results.append({'id': len(results), 'value': row.get('name'), 'url': row.get('url')})

    return jsonify(results)

@app.route('/<path:filename>')
def static_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
