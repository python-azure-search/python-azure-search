import json
from .connection import Endpoint
from .document import Documents

class Field(object):
    # "name": "name_of_field",  
    # "type": "Edm.String | Collection(Edm.String) | Edm.Int32 | Edm.Int64 | Edm.Double | Edm.Boolean | Edm.DateTimeOffset | Edm.GeographyPoint",  
    # "searchable": true (default where applicable) | false (only Edm.String and Collection(Edm.String) fields can be searchable),  
    # "filterable": true (default) | false,  
    # "sortable": true (default where applicable) | false (Collection(Edm.String) fields cannot be sortable),  
    # "facetable": true (default where applicable) | false (Edm.GeographyPoint fields cannot be facetable),  
    # "key": true | false (default, only Edm.String fields can be keys),  
    # "retrievable": true (default) | false,  
    # "analyzer": "name of the analyzer used for search and indexing", (only if 'searchAnalyzer' and 'indexAnalyzer' are not set)
    # "searchAnalyzer": "name of the search analyzer", (only if 'indexAnalyzer' is set and 'analyzer' is not set)
    # "indexAnalyzer": "name of the indexing analyzer" (only if 'searchAnalyzer' is set and 'analyzer' is not set)
    name = None
    _field_type = None
    python_type = None # Why python type is this?
    searchable = False  # only Edm.String and Collection(Edm.String) fields can be searchable
    filterable = True  
    sortable = True
    facetable = False
    key = False
    retrievable = False

    def __init__(self,
        name, index=None, retrievable=True, sortable=True, facetable=True, filterable=True, **kwargs):
        self.name = name
        self.retrievable = retrievable
        self.retrievable = facetable
        self.filterable = filterable
        self.sortable = sortable

    def __repr__(self):
        return "<Azure{cls} : {index}.{name}>".format(
            cls=self.__class__.__name__, index=self.index.name, name=self.name
        )

    @property
    def field_type(self):
        if self._field_type:
            return self._field_type
        else:
            return "Edm.{}".format(self.__class__.__name__.replace('Field',""))

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.field_type,
            "searchable": self.searchable,
            "filterable": self.filterable,
            "sortable": self.sortable,
            "facetable": self.facetable,
            "key": self.key,
            "retrievable": self.retrievable,
            # "analyzer": self.analyzer,
            # "searchAnalyzer": self.searchAnalyzer,
            # "indexAnalyzer": self.indexAnalyzer,
        }

    @classmethod
    def load(cls, data, **kwargs):
        if type(data) is str:
            data = json.loads(data)
        if type(data) is not dict:
            raise Exception  # TODO: Exception here
        
        field_type = types[data.pop('type')]
        kwargs.update(data)
        return field_type(**kwargs)
        
        

class StringField(Field):
    python_type = str
    def __init__(self, name, searchable=True, key=False, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.key = key
        self.searchable = searchable
class CollectionField(Field):
    _field_type = "Collection(Edm.String)"
    def __init__(self, name, searchable=True, key=False, *args, **kwargs):
        kwargs['sortable'] = False
        super().__init__(name, *args, **kwargs)
        self.searchable = searchable
class Int32Field(Field):
    python_type = int
class Int64Field(Field):
    python_type = int
class DoubleField(Field):
    python_type = float
class BooleanField(Field):
    python_type = bool
class DateTimeOffsetField(Field):
    python_type = None
class GeographyPointField(Field):
    def __init__(self, name, facetable=False, *args, **kwargs):
        kwargs['facetable'] = False  # Edm.GeographyPoint fields cannot be facetable
        super().__init__(name, *args, **kwargs)


class Index(object):
    endpoint = Endpoint("indexes")
    results = None

    def __init__(self, name, fields=[], suggesters=[], analysers=[]):
        self.name = name
        self.fields = fields
        for f in self.fields:
            f.index = self
        self.documents = Documents(self)

    def __repr__(self):
        return "<AzureIndex: {name}>".format(
            name=self.name
        )

    def to_dict(self):
        return {
         "name": self.name,  
         "fields": [field.to_dict() for field in self.fields],
        #  "suggesters": [
        #   {
        #   "name": "sg",
        #   "searchMode": "analyzingInfixMatching",
        #   "sourceFields": ["hotelName"]
        #   }
        #  ],
        #  "analyzers": [
        #   {
        #   "name": "tagsAnalyzer",
        #   "@odata.type": "#Microsoft.Azure.Search.CustomAnalyzer",
        #   "charFilters": [ "html_strip" ],
        #   "tokenizer": "standard_v2"
        #   }
        #  ]
        }

    @classmethod
    def load(cls, data):
        if type(data) is str:
            data = json.loads(data)
        if type(data) is not dict:
            raise Exception  # TODO: Exception here
        return cls(name=data['name'], fields=[Field.load(f) for f in data['fields']])

    def create(self):
        return self.endpoint.post(self.to_dict())

    def update(self):
        self.delete()
        return self.create()

    def delete(self):
        return self.endpoint.delete(endpoint=self.name)

    @classmethod
    def list(cls):
        return cls.endpoint.get()

    def search(self, query):
        query = {
            "search": query,
            "queryType": "full",  
            "searchMode": "all"  
        }
        print(query)
        self.results = self.endpoint.post(query, endpoint=self.name+"/docs/search")
        return self.results

types = {
    "Edm.String": StringField, 
    "Collection(Edm.String)": CollectionField, 
    "Edm.Int32": Int32Field,
    "Edm.Int64": Int64Field,
    "Edm.Double": DoubleField,
    "Edm.Boolean": BooleanField,
    "Edm.DateTimeOffset": DateTimeOffsetField,
    "Edm.GeographyPoint": GeographyPointField
}