#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
"""

from __future__ import absolute_import

import logging
import pickle

import apache_beam as beam

from apache_beam.io import iobase
from apache_beam.transforms import DoFn
from apache_beam.transforms import PTransform
from apache_beam.transforms import Reshuffle
from apache_beam.utils.annotations import experimental

import redis

__all__ = ['WriteToRedis']

@experimental()
class WriteToRedis(beam.PTransform):
    """
    """
    
    def __init__(self, host='localhost', port=6379, batch_size=100):
        """
        """
        self._host = host
        self._port = port
        self._batch_size = batch_size

    def expand(self, pcoll):
        return pcoll \
               | Reshuffle() \
               | beam.ParDo(_WriteRedisFn(self._host, self._port,
                                          self._batch_size))

class _WriteRedisFn(DoFn):

    def __init__(self, host, port, batch_size):
        self.host = host
        self.port = port
        self.batch_size = batch_size

        self.batch_counter = 0
        self.batch = list()

    def finish_bundle(self):
        self._flush()

    def process(self, element, *args, **kwargs):
        self.batch.append(element)
        self.batch_counter += 1
        if self.batch_counter == self.batch_size:
            self._flush()
            
    def _flush(self):
        if self.batch_counter == 0:
            return

        with _RedisSink(self.host, self.port) as sink:
            sink.write(self.batch)
            self.batch_counter = 0
            self.batch = list()

    def display_data(self):
        res = super(_WriteRedisFn, self).display_data()
        res['host'] = self.host
        res['port'] = self.port
        res['batch_size'] = self.batch_size
        return res
            
class _RedisSink(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = None

    def _create_client(self):
        if self.client is None:
            self.client = redis.StrictRedis(host=self.host,
                                            port=self.port)

    def write(self, elements):
        self._create_client()
        with self.client.pipeline() as pipe:
            for element in elements:
                k,v = element
                pipe.set(k,v)
            logging.debug('writing to redis')
            pipe.execute()
            
    def __enter__(self):
        self._create_client()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client is not None:
            self.client.close()
