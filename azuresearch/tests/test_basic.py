import requests
import os
import json
from nose import with_setup
from time import sleep
import unittest
from haikunator import Haikunator
haikunator = Haikunator()

path = os.path.dirname(os.path.abspath(__file__))

def get_json_file(name):
    return json.load(open(os.path.join(path,'test_objects',name)))


from azuresearch import indexes

def test_azure():
    index = indexes.Index.load(get_json_file("hotels.index.json"))

def setup_indexes():
    "Remove any indexes in the engine"
    for index in indexes.Index.list().json()['value']:
        indexes.Index(name=index['name']).delete()
    index_list = indexes.Index.list().json()
    assert len(index_list['value']) == 0


def teardown_indexes():
    for index in indexes.Index.list().json()['value']:
        indexes.Index(name=index['name']).delete()
    index_list = indexes.Index.list().json()
    assert len(index_list['value']) == 0


@with_setup(setup_indexes, teardown_indexes)
def test_index_create():
    index_list = indexes.Index.list().json()
    assert len(index_list['value']) == 0

    index = indexes.Index.load(get_json_file("hotels.index.json"))
    # print("Update index in Azure -----------------")
    result = index.update()
    #  https://docs.microsoft.com/en-us/rest/api/searchservice/create-index#response
    #  For a successful request, you should see status code "201 Created".
    assert result.status_code == 201  #

    index_list = indexes.Index.list().json()
    assert len(index_list['value']) == 1
    assert index_list['value'][0]['name'] == "hotels"



class TestHotels(unittest.TestCase):
    def setUp(self):
        setup_indexes()
        hotels_index = indexes.Index.load(get_json_file("hotels.index.json"))
        name = haikunator.haikunate()
        hotels_index.name = name
        hotels_index.update()
        hotels_index.documents.add(get_json_file("hotels.documents.json"))
        results = hotels_index.count()
        for i in range(8):
            sleep(0.5)
            count = hotels_index.count()
            print(count)
            if count == 4:
                break
        else:
            # Try one last time
            count = hotels_index.count()
            print(count)
            assert count == 4
        self.index = hotels_index


    def test_search(self):
        results = self.index.search("expensive").json()
        print("Results were", len(results['value']), results)
        assert len(results['value']) == 2
    
        results = self.index.search("memorable").json()
        print("Results were", len(results['value']), results)
        assert len(results['value']) == 1
    
        results = self.index.search("expensive").json()
        print("Results were", len(results['value']), results)
        assert len(results['value']) == 2


def extra():
    # from azuresearch.connection import Endpoint
    # e = Endpoint("")
    # r=e.post(endpoint="indexes/hotels/docs/search")
    # print(r)
    # requests.get(
    #     "https://django-haystack-azure-search.search.windows.net/indexes/hotels/docs/search"
    # )
    
    print("Cleanup -----------------")
    i = index.delete()
    print(i.status_code)
    print(i.text)
