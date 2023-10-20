from abc import ABC, abstractmethod
from pelix.ipopo.decorators import Requires
from flask import Flask
import threading
from typing import Dict, List, Type, Union
from rdflib import Graph, RDF, URIRef, Literal, Namespace
import uuid
from rdflib.namespace import DCTERMS, DCAT, XSD, DefinedNamespace
import json
import re
import logging
from collections import OrderedDict
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID


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
        
class MetadataConf(Input):
    
    def __init__(self, graph_id: str, dataset_id: str, distribution_id: str, configuration: str):
        self.__graph_id = graph_id
        self.__dataset_id = dataset_id
        self.__distribution_id = distribution_id
        self.__configuration = configuration
        
    @property
    def graph_id(self) -> Reference:
        return self.__graph_id
    
    @property
    def dataset_id(self) -> Reference:
        return self.__dataset_id
    
    @property
    def distribution_id(self) -> Reference:
        return self.__distribution_id
    
    @property
    def configuration(self) -> Reference:
        return self.__configuration
    
    @staticmethod
    def from_dict(d: Dict) -> Input:
        
        dict_keys = ['id', 'dataset_id', 'distribution_id', 'configuration']
        
        for dict_key in dict_keys:
            if dict_key not in d:
                raise MissingKeyInDictionary('id')
        
        graph_id = Reference(d['id'])
        dataset_id = Reference(d['dataset_id'])
        distribution_id = Reference(d['distribution_id'])
        configuration = Reference(d['configuration']) 
        
        return MetadataConf(graph_id, dataset_id, distribution_id, configuration)
            

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
        
        logging.info(f'Input contains {dict}')
        if 'graphs' in dict:
            mapping_confs = [MappingConf.from_dict(conf) for conf in dict['graphs']]
        else:
            raise MissingKeyInDictionary('graphs') 
        
        return MapperInput(input.data_sources, mapping_confs)
    
    
class MetadataInput(Input):
    
    def __init__(self, metadata_confs: List[MetadataConf]):
        self.__metadata_confs = metadata_confs
        
    @property
    def metadata_confs(self):
        return self.__metadata_confs

    @staticmethod
    def from_dict(dict: Dict) -> 'MetadataInput':
        
        print(f'Input contains {dict}')
        if 'meta' in dict:
            metadata_confs = [MetadataConf.from_dict(conf) for conf in dict['meta']]
        else:
            raise MissingKeyInDictionary('meta')
        
        return MetadataInput(metadata_confs)
    
class ValidatorConfiguration(Input):
    
    def __init__(self, graph_id: Reference, graph_uri: Reference):
        self.__graph_id = graph_id
        self.__graph_uri = graph_uri
        
    @property
    def graph_id(self) -> Reference:
        return self.__graph_id
    
    @property
    def graph_uri(self) -> Reference:
        return self.__graph_uri

    @staticmethod
    def from_dict(dict: Dict) -> 'ValidatorConfiguration':
        
        if 'id' and 'uri' in dict:
            return ValidatorConfiguration(dict['id'], dict['uri'])
        else:
            raise MissingKeyInDictionary('id or uri')
        
    
class ValidatorInput(Input):
    
    def __init__(self, confs: List[ValidatorConfiguration]):
        self.__confs = confs
        
    @property
    def confs(self):
        return self.__confs

    @staticmethod
    def from_dict(dict: Dict) -> 'ValidatorInput':
        
        if 'metadata' in dict:
            confs = [ValidatorConfiguration(conf['id'], conf['uri']) for conf in dict['metadata']]
        else:
            raise MissingKeyInDictionary('metadata')
        
        return ValidatorInput(confs)
    

'''    
class MetadataInput(Input):
    
    NAMESPACES = {'dcat': DCAT, 
              'dct': DCTERMS, 
              'dcterms': DCTERMS, 
              'terms': DCTERMS}
    
    def __init__(self, dataset: Dict[str,str], distribution: Dict[str,str]):
        
        self.__properties = dict()
        
        self.__dataset = Graph()
        self.__distro = Graph()
        
        for k,v in dataset.items():
            prop = self.__get_uriref(k)
            if prop in DCAT or prop in DCTERMS:
                val = self.__get_rdfterm(v)
                if val:
                    
            else:
                raise ValueError("Illegal DCAT o DCT property: ", prop)
    
    def __get_rdfterm(self, term: str) -> Union[URIRef, Literal]:
        if term[0] == '<' and terms[-1:] == '>':
            return URIRef(term[1:-2])
        else:
            pattern = '(\'|")(.*)(\'|")(@([a-z]+)|(\^\^(.*)))?'
            
            m = re.match(pattern, term)
            if m:
                lexical_form = m.group(2)
                lang = m.group(5)
                dtype = m.group(7)
                
                if lang:
                    return Literal(term, lang=lang)
                elif dtype:
                    
                    dtype = self.__get_uriref(dtype)
                    return Literal(term, datatype=dtype)
                else:
                    return Literal(term)
                    
            else:
                return None
    
    def __get_uriref(self, term: str) -> URIRef:
        prop = None
        
        if term[0] == '<' and terms[-1:] == '>':
            prop = URIRef(term[1:-2])
        else:
            parts = term.split(':')
            if len(parts) == 2:
                prefix = parts[0]
                prop_id = parts[1]
            
                if prefix in NAMESPACES:
                    prop = NAMESPACES[prefix][prop_id]
                else:
                    prop = URIRef(term)
                
            else:
                prop = URIRef(term)
        
        return prop
      
        
        
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
'''

class ToolkitComponent(ABC):
    
    @abstractmethod
    def do_job(self, input: Input, *args, **kwargs):
        pass
    
    @abstractmethod
    def depends_on(self) -> List[Type['ToolkitComponent']]:
        pass


class Ingester(ToolkitComponent):
    
    def do_job(self, input: Graph, store=True):
        pass
    
    def depends_on(self) -> List[Type['ToolkitComponent']]:
        return []

class DataPreprocessor(ToolkitComponent):
    
    @abstractmethod
    def do_job(self, input: DataCollection, *args, **kwargs):
        pass
    
    def depends_on(self) -> List[Type['ToolkitComponent']]:
        return [Ingester]

class Mapper(ABC):
    
    @abstractmethod
    def do_job(self, input: MapperInput, *args, **kwargs):
        pass
    
    def depends_on(self) -> List[Type['ToolkitComponent']]:
        return [DataPreprocessor]
    
class MetadataCreator(ABC):
    
    @abstractmethod
    def do_job(self, input: MetadataInput, *args, **kwargs):
        pass
    
    def depends_on(self) -> List[Type['ToolkitComponent']]:
        return [Mapper]
    
class Validator(ABC):
    
    @abstractmethod
    def do_job(self, input: ValidatorInput, *args, **kwargs):
        pass
    
    def depends_on(self) -> List[Type['ToolkitComponent']]:
        return [MetadataCreator]
    
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
        RESTApp.host = '0.0.0.0'
        RESTApp.port = port
    
    @classmethod
    def get_flask_app(cls):
        if not cls.instance:
            
            print(f'Webserver port {RESTApp.port}')
            cls.instance = Flask('__name__')
            #cls.instance.run(port=RESTApp.port)
            
            threading.Thread(target=lambda: cls.instance.run(host=RESTApp.host, port=RESTApp.port)).start()
            
            
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
        
class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if key in self:
            if isinstance(value, list):
                self[key].extend(value)
                return
            elif isinstance(value,str):
                return # ignore conversion list to string (line 554)
        super(MultiOrderedDict, self).__setitem__(key, value)


class MalformedRDFTerm(Exception):
    
    def __init__(self, key, message="The RDF term {0} is malformed."):
        self.key = key
        self.message = message.format(key)
        super().__init__(self.message)

class RDFTermFactory():
    
    NAMESPACES = {
        'dct': DCTERMS,
        'dcterms': DCTERMS,
        'terms': DCTERMS,
        'dcat': DCAT,
        'xsd': XSD
    }
    
    @staticmethod
    def create_rdf_term(term):
        
        try:
            rdfterm = RDFTermFactory.create_uri(term)
        except MalformedRDFTerm as e:
            rdfterm = RDFTermFactory.create_literal(term)
            
        return rdfterm 
            
    
    @staticmethod
    def create_uri(uri):
    
        if uri[0] == '<' and uri[-1] == '>':
            return URIRef(uri[1:-2])
        elif ':' in uri:
            prefix, id = uri.split(':')
            if prefix in RDFTermFactory.NAMESPACES:
                return RDFTermFactory.NAMESPACES[prefix][id]
        else:
            raise MalformedRDFTerm(uri)

    @staticmethod        
    def create_literal(literal):
        
        pattern_lexical_value = '(\'|")(.*)(\'|")'
        pattern_language = '@([a-z]{2})$'
        pattern_datatype = '\^\^(.*)$'
        
        #me = re.match(pattern, '\questo è un testo\'@it')
        
        me = re.search(pattern_lexical_value, literal)
        if me:
            lexical_value = me.group(2)
            
            me = re.search(pattern_language, literal)
            if me:
                return Literal(lexical_value, lang=me.group(1))
            else:
                me = re.search(pattern_datatype, literal)
                if me:
                    datatype = me.group(1)
                    datatype = get_uri(datatype)
                    
                    return Literal(lexical_value, datatype=datatype)
                else:
                    return Literal(lexical_value)
            
        else:
            raise MalformedRDFTerm(literal)
    
    