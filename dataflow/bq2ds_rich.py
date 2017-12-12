#!/usr/bin/env python

import uuid
import datetime
import re
from copy import deepcopy

import apache_beam as beam
from googledatastore import helper
from google.cloud.proto.datastore.v1 import entity_pb2
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions, StandardOptions
from apache_beam.io.gcp.datastore.v1.datastoreio import WriteToDatastore

options = PipelineOptions(flags=['--save_main_session',
                                 '--requirements_file=requirements.txt'])
google_cloud_options = options.view_as(GoogleCloudOptions)
google_cloud_options.project = 'sample-datalab'
google_cloud_options.job_name = ("autocomplete-genkey-%s" % datetime.datetime.today().strftime("%m%dt%H%M"))
google_cloud_options.staging_location = 'gs://heita-datalab-dataflow/binaries'
google_cloud_options.temp_location = 'gs://heita-datalab-dataflow/temp'
options.view_as(StandardOptions).runner = 'DataflowRunner'
  
def new_elm(element, key):
    elm = deepcopy(element)
    elm['key'] = key
    return elm

def gen_key(element):
    # fix up data
    for k,v in element.items():
        if v is None:
            del(element[k])
  
    # generate word-prefix for each words as keys
    result = []
    key = element['name'].upper()
    while key != '':
        for i in range(2, len(key) + 1):
            result.append(new_elm(element, key[0:i]))
        key = re.sub('\\S+\\s*\\W*', '', key, count=1)
    return result

class EntityWrapper(object):
  def __init__(self, namespace, kind):
    self._namespace = namespace
    self._kind = kind

  def make_entity(self, content):
    entity = entity_pb2.Entity()
    if self._namespace is not None:
      entity.key.partition_id.namespace_id = self._namespace

    helper.add_key_path(entity.key, self._kind, str(uuid.uuid4()))
    helper.add_properties(entity, content)
    return entity

p = beam.Pipeline(options=options)
(p | 'query from bq'       >> beam.io.Read(beam.io.BigQuerySource(query="select * from bestbuy.products"))
   | 'generate key'        >> beam.FlatMap(gen_key)
   | 'make entry'          >> beam.Map(EntityWrapper(None, 'products3').make_entity)
   | WriteToDatastore("sample-datalab")
)
p.run()

