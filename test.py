import requests
import os
import json

os.environ['AZURE_SEARCH_API_KEY'] = '5383BA7109ECB93848760CD22CF547F9'


os.environ['AZURE_SEARCH_URL'] = 'https://django-haystack-azure-search.search.windows.net'

index_data = json.load(open('./azuresearch/test_objects/hotels.index.json'))
document_data = json.load(open('./azuresearch/test_objects/hotels.documents.json'))

from azuresearch import indexes

print("Create Python Index -----------------")
index = indexes.Index.load(index_data)

print("Update index in Azure -----------------")
print(index.update().text)

print("List indexes from Azure -----------------")
index_list = indexes.Index.list().json()
assert len(index_list['value']) == 1

print("Load documents into Azure -----------------")
response = index.documents.add(document_data)
print(response.text)

# print(index.update().text)
print("Query -----------------")
results = index.search("expensive")
print(results)
print(results.text)

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
