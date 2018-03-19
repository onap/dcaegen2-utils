# org.onap.dcae
# ============LICENSE_START====================================================
# Copyright (c) 2018 AT&T Intellectual Property. All rights reserved.
# =============================================================================
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============LICENSE_END======================================================
#
# ECOMP is a trademark and service mark of AT&T Intellectual Property.

import base64
import json
import os
import requests
from threading import Thread
import uuid
from onap_dcae_cbs_docker_client.client import get_config

try:
  from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:
  from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

_httpport = int(os.environ['DCAEPORT']) if 'DCAEPORT' in os.environ else 80
_clientid = uuid.uuid4().hex
_groupid = uuid.uuid4().hex

class _handler(BaseHTTPRequestHandler):
  def do_GET(self):
    if '/healthcheck' == self.path:
      if self.server.env._health():
        self.send_response(202)
        self.end_headers()
      else:
        self.send_error(503)
    elif '/reconfigure' == self.path:
      self.server.env._loadconfig()
      self.server.env._reconf()
      self.send_response(202)
      self.end_headers()
    else:
      self.send_error(404)

def _genauth(sinfo):
  """
  Return authentication parameters for stream, if present.
  """
  user = sinfo['aaf_username'] if 'aaf_username' in sinfo else None
  password = sinfo['aaf_password'] if 'aaf_password' in sinfo else None
  if user and password:
    return { 'auth': (user, password) }
  else:
    return {}

class DcaeEnv:
  def __init__(self, healthCB = lambda:True, reconfigCB = lambda:None):
    """
    Initialize environment, but don't start web server or invoke any callbacks.
    """
    self._health = healthCB
    self._reconf = reconfigCB
    self._unread = {}
    self._server = None
    self._loadconfig()

  def start(self):
    """
    Start web server to receive health checks and reconfigure requests
    """
    if self._server is not None:
      return
    self._server = HTTPServer(('', _httpport), _handler)
    self._server.env = self
    th = Thread(target=self._server.serve_forever, name='webserver')
    th.daemon = True
    th.start()

  def stop(self):
    """
    Stop web server
    """
    if self._server is None:
      return
    self._server.shutdown()
    self._server.env = None
    self._server = None

  def _loadconfig(self):
    self._config = get_config()

  def hasdata(self, stream):
    """
    Return whether there is any unprocessed received data for the specified
    data stream.  That is, if an earlier getdata() call returned more than
    one record, and the additional records have not yet been retrieved.
    """
    return stream in self._unread

  def getdata(self, stream, timeout_ms = 15000, limit = 10):
    """
    Try to retrieve data from Message Router for the specified data stream.
    If no data is retrieved, within the specified timeout, return None.
    """
    sinfo = self._config['streams_subscribes'][stream]
    if stream in self._unread:
      x = self._unread[stream]
      ret = x.pop()
      if len(x) == 0:
        del self._unread[stream]
      return ret
    gid = sinfo['client_id'] if 'client_id' in sinfo and sinfo['client_id'] else _groupid
    resp = requests.get('{0}/{1}/{2}?timeout={3}&limit={4}'.format(sinfo['dmaap_info']['topic_url'], gid, _clientid, timeout_ms, limit), **_genauth(sinfo))
    resp.raise_for_status()
    x = resp.json()
    if len(x) == 0:
      return None
    if len(x) == 1:
      return x[0]
    x.reverse()
    ret = x.pop()
    self._unread[stream] = x
    return ret

  def senddata(self, stream, partition, data):
    """
    Publish data to the specified stream.
    """
    sinfo = self._config['streams_publishes'][stream]
    body = '{0}.{1}.{2}{3}'.format(len(partition), len(data), partition, data)
    resp = requests.post('{0}'.format(sinfo['dmaap_info']['topic_url']), headers={'Content-Type': 'application/cambria'}, data=body, **_genauth(sinfo))
    resp.raise_for_status()

  def getconfig(self):
    """
    Get the latest version of the configuration data.
    """
    return self._config

def reconfigure():
  """
  Make the web request to reconfigure (locally)
  """
  requests.get('http://localhost:{0}/reconfigure'.format(_httpport))
