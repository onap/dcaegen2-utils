from onap_dcae_cbs_docker_client.client import get_config
import requests

class FakeResponse:
    def __init__(self, status_code, thejson):
        self.status_code = status_code
        self.thejson = thejson
    def raise_for_status(self):
        pass
    def json(self):
        return self.thejson

def test_client(monkeypatch):

    def monkeyed_requests_get(url):
        #mock all the get calls for existent and non-existent
        if url == "http://consuldotcom:8500/v1/catalog/service/config_binding_service":
            return FakeResponse(
                       status_code = 200,
                       thejson = [
                           {"ServiceAddress" : "666.666.666.666",
                            "ServicePort" : 8888
                           }]
                )
        elif url == "http://666.666.666.666:8888/service_component/mybestfrienddotcom":
            return FakeResponse(
                       status_code = 200,
                       thejson = {"key_to_your_heart" : 666})


    monkeypatch.setattr('requests.get', monkeyed_requests_get)
    assert(get_config() == {"key_to_your_heart" : 666})




