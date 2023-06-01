import os
import uuid

from pelix.ipopo.decorators import Validate, ComponentFactory, Property, Provides, Instantiate
from rdflib.graph import Graph, URIRef, Literal
from rdflib.namespace._DCAT import DCAT
from rdflib.namespace._DCTERMS import DCTERMS
from rdflib.namespace._RDF import RDF

from api.api import Configuration, MetadataCreator, MetadataInput 
from rdflib.namespace._RDFS import RDFS


@ComponentFactory("metadata-factory")
@Property('_graphs_location', 'graphs.location', '')
@Property('_http_endpoint', 'http.endpoint', '')
@Provides("metadata")
@Instantiate("dcat_metadata_creator")
class DCATMetadataCreator(MetadataCreator):
    
    
    
    @Validate
    def validate(self, context):
        
        self.__conf = Configuration('./metadata/conf/props.json')
        self._graphs_location = self.__conf.get_property('graphs.location')
        self._http_endpoint = self.__conf.get_property('http.endpoint')
        
        if not os.path.exists(self._graphs_location):
            os.makedirs(self._graphs_location)
    
    
    
    '''
    Input
    '''
    def create_metadata(self, input: MetadataInput, *args, **kwargs):
        
        g = Graph()
        
        _id = str(uuid.uuid4())
        
        distro =  URIRef(input.distribution.uri) if input.distribution else URIRef(f'{self._http_endpoint}distribution/{_id}')
        dset =  URIRef(input.dataset.uri) if input.dataset else URIRef(f'{self._http_endpoint}dataset/{_id}')
        url =  URIRef(input.access_url.uri) if input.access_url else URIRef(f'{self._http_endpoint}graph/{_id}')
        title = Literal(input.title)
        description = Literal(input.description)
        
        g.add((dset, RDF.type, DCAT.Dataset))
        g.add((dset, DCAT.distribution, distro))
        g.add((distro, RDF.type, DCAT.Distribution)) 
        g.add((distro, DCTERMS.title, title))
        g.add((distro, RDFS.label, title))
        g.add((distro, DCTERMS.description, description))
        g.add((distro, RDFS.comment, description))
        g.add((distro, DCAT.accessURL, url))

        return g
                