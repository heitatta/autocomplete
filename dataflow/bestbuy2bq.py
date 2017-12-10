#!/usr/bin/env python
"""
suppose big query talbe exists by:
  bq mk bestbuy
"""

import apache_beam as beam
import datetime
import time
import requests
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions, StandardOptions

# --requirements_file requirements.txt

# Create and set your PipelineOptions.
options = PipelineOptions(flags=['--save_main_session',
                                 '--requirements_file=requirements.txt'])

# For Cloud execution, set the Cloud Platform project, job_name,
# staging location, temp_location and specify DataflowRunner.
google_cloud_options = options.view_as(GoogleCloudOptions)
google_cloud_options.project = 'sample-datalab'
google_cloud_options.job_name = ("autocomplete-raw-%s" % datetime.datetime.today().strftime("%m%dt%H%M"))
google_cloud_options.staging_location = 'gs://heita-datalab-dataflow/binaries'
google_cloud_options.temp_location = 'gs://heita-datalab-dataflow/temp'
options.view_as(StandardOptions).runner = 'DataflowRunner'


def fetch_data(api_key):
  page_size = 100
  cursor_mark = "*"
  while(True):
    for i in range(0,10):
      res = requests.get("https://api.bestbuy.com/v1/products?format=json&" +\
                         "cursorMark=%s&show=name,releaseDate,bestSellingRank,url&pageSize=%d&apiKey=%s"
                         % (cursor_mark, page_size, api_key))
      if res.status_code == 200:
          break
      time.sleep(1)
    products = res.json()
    if 'products' not in products or len(products['products']) == 0:
        break
    for product in products['products']:
        if product['bestSellingRank'] is None:
            product['bestSellingRank'] = 0
        yield(product)
    cursor_mark = products['nextCursorMark']

def id_func(arg):
  return arg


p = beam.Pipeline(options=options)
(p | 'api key'         >> beam.Create(['pHRhgOkDJ8cmKCmKKoYwPDH3'])
   | 'fetch data'      >> beam.FlatMap(fetch_data)
   | 'id dummy'        >> beam.Map(id_func)
   | 'write to bq'     >> beam.io.Write(beam.io.BigQuerySink('bestbuy.products2',
                              schema="name:STRING, releaseDate:DATE, bestSellingRank:INTEGER",
                              write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                              create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED))
)
p.run() #.wait_until_finish()
