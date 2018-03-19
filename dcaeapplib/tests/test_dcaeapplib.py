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

import dcaeapplib
import requests
import json

class Stubs:
  def __init__(self):
    self.toreturn = [ 's1', 's2', 's3' ]
    self.config = {
        "anotherparameter": 1,
        "streams_subscribes": {
          "myinputstream": {
            "aaf_username": "user1",
            "aaf_password": "pass1",
            "dmaap_info": {
              "topic_url": "http://messagerouter.example.com:3904/events/topic1"
            }
          }
        },
        "streams_publishes": {
          "myoutputstream": {
            "aaf_username": None,
            "aaf_password": None,
            "dmaap_info": {
              "topic_url": "http://messagerouter.example.com:3904/events/topic2"
            }
          }
        }
      }
    self.health = True
    self.cc = False

  def raise_for_status(self):
    pass

  def json(self):
    return self.toreturn

def test_todo(monkeypatch):
  stuff = Stubs()
  def stub_config():
    return json.loads(json.dumps(stuff.config))
  def stub_hc():
    return stuff.health
  def stub_cc():
    stuff.cc = True
  monkeypatch.setattr(dcaeapplib, 'get_config', stub_config)
  monkeypatch.setattr(dcaeapplib, '_httpport', 0)
  env = dcaeapplib.DcaeEnv(healthCB=stub_hc, reconfigCB=stub_cc)
  env.stop() # exercise stop when not running
  env.start()
  print('Port is {0}'.format(env._server.server_port))
  monkeypatch.setattr(dcaeapplib, '_httpport', env._server.server_port)
  stuff.config['anotherparameter'] = 2
  assert env.getconfig()['anotherparameter'] == 1
  dcaeapplib.reconfigure()
  assert stuff.cc is True
  assert env.getconfig()['anotherparameter'] == 2
  resp = requests.get('http://localhost:{0}/healthcheck'.format(dcaeapplib._httpport))
  assert resp.status_code < 300
  stuff.health = False
  resp = requests.get('http://localhost:{0}/healthcheck'.format(dcaeapplib._httpport))
  assert resp.status_code >= 500
  resp = requests.get('http://localhost:{0}/invalid'.format(dcaeapplib._httpport))
  assert resp.status_code == 404
  env.start() # exercise start when already running
  env.stop()
  def stub_get(*args, **kwargs):
    stuff.auth = 'auth' in kwargs
    return stuff
  def stub_post(url, data, *args, **kwargs):
    assert data == '4.11.asdfhello world'
    stuff.auth = 'auth' in kwargs
    stuff.posted = True
    return stuff
  monkeypatch.setattr(requests, 'post', stub_post)
  stuff.posted = False
  stuff.auth = True
  env.senddata('myoutputstream', 'asdf', 'hello world')
  assert stuff.posted == True
  assert stuff.auth == False
  monkeypatch.setattr(requests, 'get', stub_get)
  assert env.hasdata('myinputstream') is False
  assert env.getdata('myinputstream') == 's1'
  assert stuff.auth == True
  stuff.toreturn = [ 'a1' ]
  assert env.getdata('myinputstream') == 's2'
  assert env.hasdata('myinputstream') is True
  assert env.getdata('myinputstream') == 's3'
  assert env.hasdata('myinputstream') is False
  assert env.getdata('myinputstream') == 'a1'
  stuff.toreturn = []
  assert env.hasdata('myinputstream') is False
  assert env.getdata('myinputstream') is None
