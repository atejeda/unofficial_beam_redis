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
"""This module implements IO classes to read write data on Redis.


Write to Redis:
-----------------
:class:`WriteToRedis` is a ``PTransform`` that writes key and values to a 
configured sink, and the write is conducted through a redis pipeline. 

The ptransform works by getting the first and second elements from the input,
this means that inputs like `[k,v]` or `(k,v)` are valid.

Example usage::

  pipeline | WriteToRedis(host='localhost',
                          port=6379,
                          batch_size=100)


No backward compatibility guarantees. Everything in this module is experimental.
"""

from __future__ import absolute_import

import logging
import pickle

from past.builtins import unicode

import apache_beam as beam

from apache_beam.io import iobase
from apache_beam.transforms import DoFn
from apache_beam.transforms import PTransform
from apache_beam.transforms import Reshuffle
from apache_beam.utils.annotations import experimental
from apache_beam.options.value_provider import ValueProvider
from apache_beam.options.value_provider import StaticValueProvider

import redis

__all__ = ['WriteToRedis']

@experimental()
class WriteToRedis(beam.PTransform):
    """WriteToRedis is a ``PTransform`` that writes a ``PCollection`` of
    key, value tuple or 2-element array into a redis server.
    """
    
    def __init__(self, host=None, port=None, command=None, batch_size=100):
        """

        Args:
        host (str, ValueProvider): The redis host
        port (int, ValueProvider): The redis port
        batch_size(int, ValueProvider): Number of key, values pairs to write at once

        Returns:
        :class:`~apache_beam.transforms.ptransform.PTransform`

        """
        if not isinstance(host, (str, unicode, ValueProvider)):
            raise TypeError(
                '%s: host must be string, or ValueProvider; got %r instead'
            ) % (self.__class__.__name__, (type(host)))

        if not isinstance(port, (int, ValueProvider)):
            raise TypeError(
                '%s: port must be int, or ValueProvider; got %r instead'
            ) % (self.__class__.__name__, (type(port)))

        if not isinstance(port, (int, ValueProvider)):
            raise TypeError(
                '%s: batch_size must be int, or ValueProvider; got %r instead'
            ) % (self.__class__.__name__, (type(batch_size)))

        if isinstance(host, (str, unicode)):
            host = StaticValueProvider(str, host)

        if isinstance(port, int):
            port = StaticValueProvider(int, port)

        if isinstance(command, int):
            command = StaticValueProvider(str, command)

        if isinstance(batch_size, int):
            batch_size = StaticValueProvider(int, batch_size)

        self._host = host
        self._port = port
        self._command = command
        self._batch_size = batch_size

    def expand(self, pcoll):
        return pcoll \
               | Reshuffle() \
               | beam.ParDo(_WriteRedisFn(self._host,
                                          self._port,
                                          self._command,
                                          self._batch_size))

class _WriteRedisFn(DoFn):

    def __init__(self, host, port, command, batch_size):
        self.host = host
        self.port = port
        self.command = command
        self.batch_size = batch_size

        self.batch_counter = 0
        self.batch = list()

    def finish_bundle(self):
        self._flush()

    def process(self, element, *args, **kwargs):
        self.batch.append(element)
        self.batch_counter += 1
        if self.batch_counter == self.batch_size.get():
            self._flush()
            
    def _flush(self):
        if self.batch_counter == 0:
            return

        with _RedisSink(self.host.get(), self.port.get()) as sink:

            if not self.command:
                sink.write(self.batch)

            else:
                sink.execute_command(self.command, self.batch)

            self.batch_counter = 0
            self.batch = list()

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
            pipe.execute()

    def execute_command(self, command, elements):
        self._create_client()
        with self.client.pipeline() as pipe:
            for element in elements:
                k,v = element
                pipe.execute_command(command, k, v)
            pipe.execute()

    def __enter__(self):
        self._create_client()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client is not None:
            self.client.close()
