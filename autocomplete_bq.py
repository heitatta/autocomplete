#!/usr/bin/env python

import os

from flask import Flask, jsonify, request, send_from_directory
from google.cloud import bigquery

app = Flask(__name__, static_folder='static')

QUERY = "select * from bestbuy.products2 where name like '%s%%'"

@app.route('/api/v1/autocomplete')
def autocomplete():
    key = request.args.get('term', '')
    if key == '':
        return jsonify({})

    bq = bigquery.Client()
    job = bq.query(QUERY % key)
    results = []
    for row in job.result():
        results.append({'id': row.name, 'value': row.name, 'url': row.name})

    return jsonify(results)

@app.route('/<path:filename>')
def static_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
