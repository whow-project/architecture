from abc import ABC, abstractmethod
from pelix.ipopo.decorators import Requires
from flask import Flask
import threading
from typing import Dict, List, Type
from rdflib import Graph, RDF, URIRef, Literal, Namespace
import uuid
from rdflib.namespace import DCTERMS, DCAT, DefinedNamespace
import json


class Reference(object):
    
    def __init__(self, uri: str):
        self.__uri = uri
    
    @property
    def uri(self) -> str:
        return self.__uri

class DataSource(object):
    
    def __init__(self, _id: str, filename: str, reference: Reference):
        self.__id = _id
        self.__filename = filename
        self.__reference = reference
        
    @property
    def identifier(self) -> str:
        return self.__id
    
    @property
    def filename(self) -> str:
        return self.__filename
    
    @property
    def reference(self) -> Reference:
        return self.__reference
    
    @staticmethod
    def from_dict(dict: Dict):
        
        if 'id' in dict:
            _id = dict['id']
        else: 
            raise MissingKeyInDictionary('id')
        
        if 'filename' in dict:
            filename = dict['filename']
        else: 
            raise MissingKeyInDictionary('filename')
        
        if 'uri' in dict:
            uri = dict['uri']
        else: 
            raise MissingKeyInDictionary('uri')
            
        return DataSource(_id, filename, Reference(uri))
        
class Input(ABC):
    
    @staticmethod
    @abstractmethod
    def from_dict(dict: Dict) -> 'Input':
        pass

class InputBuilder():
    
    @staticmethod
    def build(input: Type[Input], dict: Dict) -> Input:
        return input.from_dict(dict)
    
class DCATObject(ABC):
    
    def __init__(self, _id: URIRef, **kwargs):
        
        self._id = _id 
        self._values = kwargs
        
    @property
    def identifier(self):
        return self._id
        
    def values(self, predicate: URIRef):
        
        key = str(predicate)
        return self._values[key] if key in self._values else None
    
    def to_rdf(self):
        
        g = Graph()
        for pred, objs in self._values.items():
            for obj in objs:
                if isinstance(obj, DCATObject):
                    g += obj.to_rdf()
                    g.add((self.identifier, pred, obj.identifier))
                else:
                    try:
                        g.add((self.identifier, pred, obj))
                    except Exception as e:
                        print(f'Object {obj} with type {type(obj)}')
                        raise e
                    
        return g
                    
                    

class DCATCatalog(DCATObject):
    
    def __init__(self, descriptions: List[Literal], titles: List[Literal], _id: URIRef = None, **kwargs):
        
        _id = _id if _id else URIRef('https://w3id.org/whow/data/catalog/' + str(uuid.uuid4()))
        super().__init__(_id, **kwargs)
        self._values[DCTERMS.description] = descriptions
        self._values[DCTERMS.title] = titles

    @property
    def datasets(self):
        return self._values[DCAT.dataset] if self._values[DCAT.dataset] else None
            
    @staticmethod
    def from_rdf(catalog_iri: URIRef, dcat_graph: Graph):
        
        descriptions = [description for description in dcat_graph.objects(catalog_iri, DCTERMS.description)]
        titles = [title for title in dcat_graph.objects(catalog_iri, DCTERMS.title)]
        
        pobjs = dcat_graph.predicate_objects(catalog_iri)
        
        params = dict()
        
        for pobj in pobjs:
            p = pobj[0]
            obj = pobj[1]
            
            
            if p not in params:
                params[p] = []
            
            if p == DCAT.dataset:
                obj = DCATDataset.from_rdf(obj, dcat_graph)
                
            params[p].append(obj)
            
        return DCATCatalog(descriptions, titles, catalog_iri, **params)
    
    
    def to_rdf(self):
        
        g = super().to_rdf()
        g.add((self._id, RDF.type, DCAT.Catalog))
                    
        return g
    
    
class DCATDataset(DCATObject):
    
    def __init__(self, descriptions: List[Literal], titles: List[Literal], _id: URIRef = None, **kwargs):
        _id = _id if _id else URIRef('https://w3id.org/whow/data/dataset/' + str(uuid.uuid4()))
        super().__init__(_id, **kwargs)
        self._values[DCTERMS.description] = descriptions
        self._values[DCTERMS.title] = titles
        
    @property
    def descriptions(self):
        return self._values[DCTERMS.description]
    
    @property
    def titles(self):
        return self._values[DCTERMS.title]

    @property
    def distributions(self):
        return self._values[DCAT.distribution] if self._values[DCAT.distribution] else None
            
    @staticmethod
    def from_rdf(dataset_iri: URIRef, dcat_graph: Graph):
        
        descriptions = [description for description in dcat_graph.objects(dataset_iri, DCTERMS.description)]
        titles = [title for title in dcat_graph.objects(dataset_iri, DCTERMS.title)]
        
        pobjs = dcat_graph.predicate_objects(dataset_iri)
        
        params = dict()
        
        for pobj in pobjs:
            p = pobj[0]
            obj = pobj[1]
            
            if p not in params:
                params[p] = []
            
            if p == DCAT.distribution:
                obj = DCATDistribution.from_rdf(obj, dcat_graph)

            params[p].append(obj)
            
        return DCATDataset(descriptions, titles, dataset_iri, **params)
    
    def to_rdf(self):
        
        g = super().to_rdf()
        g.add((self._id, RDF.type, DCAT.Dataset))
                    
        return g

class DCATDistribution(DCATObject):
    
    def __init__(self, access_urls: List[URIRef], _id: URIRef = None, **kwargs):
        _id = _id if _id else URIRef('https://w3id.org/whow/data/distribution/' + str(uuid.uuid4()))
        super().__init__(_id, **kwargs)
        self._values[DCAT.accessURL] = access_urls
    
    @property
    def access_urls(self) -> List[URIRef]:
        return self._values[DCAT.accessURL]
    
    @access_urls.setter
    def access_urls(self, access_urls: URIRef):
        self._values[DCAT.accessURL] = access_urls
        
    @staticmethod
    def from_rdf(distribution_iri: URIRef, dcat_graph: Graph):
        
        access_urls = [access_url for access_url in dcat_graph.objects(distribution_iri, DCAT.accessURL)]
        
        pobjs = dcat_graph.predicate_objects(distribution_iri)
        
        params = dict()
        
        for pobj in pobjs:
            p = pobj[0]
            obj = pobj[1]
            
            if p not in params:
                params[p] = []
            
            params[p].append(obj)
            
        return DCATDistribution(access_urls, distribution_iri, **params)
    
    
    def to_rdf(self):
        
        g = super().to_rdf()
        g.add((self._id, RDF.type, DCAT.Distribution))
                    
        return g
                         
class DCATDistributionCollection():
    
    def __init__(self, _id: str, title: str, description: str, distributions: List[DCATDistribution]):
        self.__id = _id
        self.__title = title
        sefl.__description = description
        self.__distributions = distributions
        
     
    @property
    def identifier(self) -> str:
        return self.__id
    
    @property
    def title(self) -> str:
        return self.__title
    
    @property
    def description(self) -> str:
        return self.__description
    
    @property
    def distributions(self) -> List[DCATDistribution]:
        return self.__distributions
    
    def add_distribution(self, distribution: DCATDistribution) -> None:
        self.__distributions.append(distribution)
    
    
class DataCollection(Input):
    
    def __init__(self, _id: str, data_sources: List[DataSource]):
        self.__data_sources = data_sources
        self._id = _id
        
    @property
    def identifier(self):
        return self._id    
    
    @property
    def data_sources(self) -> List[DataSource]:
        return self.__data_sources
    
    @staticmethod
    def from_dict(dict: Dict) -> Input:
        
        if 'data' in dict:
            datasources = [DataSource.from_dict(data_src) for data_src in dict['data']]                
        else:
            raise MissingKeyInDictionary('data')
        
        return DataCollection(str(uuid.uuid4()), datasources)
    
    def serialize(self, dest=None):
        
        data = [{'id': data_src.identifier, 'filename': data_src.filename, 'uri': data_src.reference.uri} for data_src in self.data_sources]
        
        if dest:
            with open(dest, "w") as f:
                json.dump({'data': data}, f, indent=4)
        else:
            return json.dumps({'data': data})
                
                

class MappingConf(Input):
    
    def __init__(self, rml: List[Reference], graph_id: str):
        self.__rml = rml
        self.__graph_id = graph_id
        
        
    @property
    def rmls(self) -> List[Reference]:
        return self.__rml
    
    @property
    def graph_id(self) -> str:
        return self.__graph_id
    
    
    @staticmethod
    def from_dict(d: Dict) -> Input:
        
        lf = lambda rml_refs: [Reference(rml_ref['uri']) for rml_ref in rml_refs if 'uri' in rml_ref]
        if 'rmls' and 'id' in d:
            return MappingConf(lf(d['rmls']), d['id'])
        else:
            return None    
            

class MapperInput(DataCollection):
    
    def __init__(self, data_sources: List[DataSource], mapping_confs: List[MappingConf]):
        super().__init__(str(uuid.uuid4()), data_sources)
        self.__mapping_confs = mapping_confs
        
    @property
    def mapping_confs(self) -> MappingConf:
        return self.__mapping_confs
    
    @staticmethod
    def from_dict(dict: Dict) -> Input:
        
        input: DataCollection = InputBuilder.build(DataCollection, dict)
        
        print(f'Input contains {dict}')
        if 'graphs' in dict:
            mapping_confs = [MappingConf.from_dict(conf) for conf in dict['graphs']]
        else:
            raise MissingKeyInDictionary('graphs') 
        
        return MapperInput(input.data_sources, mapping_confs)
    
class MetadataInput(Input):
    
    def __init__(self, graph_uri: Reference, title: str, description: str, dataset: Reference = None, distribution: Reference = None, access_url: Reference = None):
        self.__graph_uri = graph_uri
        self.__title = title
        self.__description = description
        self.__dataset = dataset
        self.__distribution = distribution
        self.__access_url = access_url
        
    @property
    def graph_uri(self):
        return self.__graph_uri
    
    @property
    def title(self):
        return self.__title
    
    @property
    def description(self):
        return self.__description
    
    @property
    def dataset(self):
        return self.__dataset
    
    @property
    def distribution(self):
        return self.__distribution
    
    @property
    def access_url(self):
        return self.__access_url
    
    
    @staticmethod
    def from_dict(d: Dict) -> 'Input':
        
        return MetadataInput(**d)
     

class DataPreprocessor(ABC):
    
    @abstractmethod
    def preprocess(self, input: DataCollection, *args, **kwargs):
        pass

class Mapper(ABC):
    
    @abstractmethod
    def map(self, input: MapperInput, *args, **kwargs):
        pass
    
class MetadataCreator(ABC):
    
    @abstractmethod
    def create_metadata(self, input: MetadataInput, *args, **kwargs):
        pass
    
class MissingKeyInDictionary(Exception):
    
    def __init__(self, key, message="The key {0} cannot be found in the dictionary provided."):
        self.key = key
        self.message = message.format(key)
        super().__init__(self.message)
        
    
class Reasoner(ABC):
    
    @abstractmethod
    def do_reasoning(self):
        pass
    
class TriplestoreManager(ABC):
    
    @abstractmethod
    def load_graphs(self):
        pass
    
    @abstractmethod
    def query(self, querystr: str):
        pass
    
    @abstractmethod
    def add_graph(self, g: Graph, graph_identifier: URIRef):
        pass
    
    @abstractmethod        
    def get_graph(self, graph_identifier):
        pass
    
class SharedDrive(ABC):
    
    @abstractmethod
    def mkdir(self, path: str):
        pass
    
    @abstractmethod
    def ls(self, path: str):
        pass
    
    @abstractmethod
    def get_file(self, path: str):
        pass
    
    @abstractmethod
    def upload(self, path, data):
        pass
    
class RESTApp(object):
    
    instance = None
    port = None
    
    def __init__(self, port):
        RESTApp.port = port
    
    @classmethod
    def get_flask_app(cls):
        if not cls.instance:
            
            print(f'Webserver port {RESTApp.port}')
            cls.instance = Flask('__name__')
            #cls.instance.run(port=RESTApp.port)
            
            threading.Thread(target=lambda: cls.instance.run(port=RESTApp.port)).start()
            
            
        return cls.instance
    
    @classmethod
    def register_resource(path, *args, **kwargs):
        print(f'The resource {path} has been registered.')
        print(f'Args: {args}')
        print(f'Kwargs: {kwargs}')
        RESTApp.get_flask_app().add_url_rule(path, *args, **kwargs)
    
class WebComponent(object):
    
    def __init__(self, path):
        self._path = path
    
    @property
    def path(self):
        return self._path
    
    
class WebSocketComponent(ABC):
    
    def __init__(self, path):
        self._path = path
    
    @abstractmethod
    def execute(self, message: str, *args, **kwargs) -> str:
        pass
    
class _HTTPResource(object):
    def __init__(self, fun, path, *args, **kwargs):
        self.__fun = fun
        #RESTApp.register_resource(path=path, view_func=fun, *args, **kwargs)
        RESTApp.get_flask_app().add_url_rule(path, view_func=fun.as_view(path), *args, **kwargs)
        print(f'Args: {path}')
        print(f'Registered resource {fun}')
    
    def __call__(self, *args, **kwargs):
        return self.__fun(args, kwargs)

def HTTPResource(path, *args, **kwargs):
    def _resource(function):
        return _HTTPResource(function, path, *args, **kwargs)
    return _resource



class Configuration():
    
    def __init__(self, conf_json: str):
        with open(conf_json) as f:
            self.__js = json.load(f)
            
    def get_property(self, prop_name):
        return self.__js[prop_name]
    



class WHOWFlow(DefinedNamespace):
    
    hasFirstActivity: URIRef
    hasLastActivity: URIRef
    hasActivity: URIRef
    hasBoundService: URIRef
    isBoundServiceOf: URIRef
    
    hasNextActivity: URIRef
    hasPreviousActivity: URIRef
    
    Plan: URIRef
    Activity: URIRef
    Service: URIRef
    
    ingestion: URIRef
    preprocessing: URIRef
    triplification: URIRef
    linking: URIRef
    reasoning: URIRef
    storage: URIRef
    
    text_csv: URIRef
    text_tsv: URIRef
    application_vnd_ms_excel: URIRef
    application_json: URIRef
    application_xml: URIRef
    
    _NS = Namespace("https://w3id.org/whow/onto/flow/")
    
    
class MediaTypeRegistry(object):
    
    REGISTRY = {
        WHOWFlow.text_csv: '.csv',
        WHOWFlow.text_tsv: '.tsv',
        WHOWFlow.application_vnd_ms_excel: '.xlsx',
        WHOWFlow.application_json: '.json',
        WHOWFlow.application_xml: '.xml',
    }
    
    @classmethod
    def extension(cls, mediatype: URIRef):
        if mediatype in cls.REGISTRY:
            return cls.REGISTRY[mediatype]
        else:
            return None