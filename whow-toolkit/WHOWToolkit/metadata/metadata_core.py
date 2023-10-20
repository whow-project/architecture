import os
import uuid

from pelix.ipopo.decorators import Validate, ComponentFactory, Property, Provides, Instantiate
from rdflib.graph import Graph, URIRef, Literal
from rdflib.namespace import DCAT, DCTERMS, RDF, RDFS, Namespace

from api.api import Configuration, MetadataCreator, MetadataInput, Reference, MultiOrderedDict, RDFTermFactory

import pandas as pd 
from configparser import RawConfigParser
import requests
from typing import List

@ComponentFactory("metadata-factory")
@Property('_graphs_folder', 'graphs.folder', '')
@Property('_http_endpoint', 'http.endpoint', '')
@Provides("metadata")
@Instantiate("dcat_metadata_creator")
class DCATMetadataCreator(MetadataCreator):
    
    
    
    @Validate
    def validate(self, context):
        
        self.__conf = Configuration('./metadata/conf/props.json')
        self._rml_folder = self.__conf.get_property('rml.folder')
        self._graphs_folder = self.__conf.get_property('graphs.folder')
        self._http_endpoint = self.__conf.get_property('http.endpoint')
        
        if not os.path.exists(self._graphs_folder):
            os.makedirs(self._graphs_folder)
    
    
    
    '''
    Input
    '''
    def do_job(self, input: MetadataInput, *args, **kwargs):
        
        DCATAPIT = Namespace('http://www.dati.gov.it/onto/dcatapit#')
        
        if not os.path.exists(self._graphs_folder):
            os.makedirs(self._graphs_folder)
            
        graphs = []
        
        for conf in input.metadata_confs:
            
            id: str = str(uuid.uuid4())
            
            graph_id = conf.graph_id
            dataset_id = conf.dataset_id.uri
            distribution_id = conf.distribution_id.uri
            
            
            dcat_data_response = requests.get(conf.configuration.uri)
            dcat_data_response.encoding = 'utf-8'
            dcat_data = dcat_data_response.text
            
            cp = RawConfigParser(dict_type=MultiOrderedDict, strict=False, delimiters=('='))
            cp.read_string(dcat_data)
            
            
            if 'dataset' and 'distribution' in cp:
                g = Graph()
                dataset_res = URIRef(dataset_id)
                distribution_res = URIRef(distribution_id)
                
                g.add((dataset_res, RDF.type, DCATAPIT['Dataset']))
                g.add((dataset_res, DCAT.distribution, distribution_res))
                
                g.add((distribution_res, RDF.type, DCATAPIT['Distribution']))
                
                
                subjects = {'dataset': dataset_res, 'distribution': distribution_res}
                
                sections = ['dataset', 'distribution']
                for section in sections:
                    for dataset_prop in cp[section]:
                        rdfprop = RDFTermFactory.create_uri(dataset_prop)
                        
                        rdfvalues = self.__create_rdf_values(cp[section][dataset_prop])
                        for rdfvalue in rdfvalues:
                            g.add((subjects[section], rdfprop, rdfvalue))
                
                
                endpoint = self._http_endpoint if self._http_endpoint.endswith('/') else self._http_endpoint + '/'
                graphs.append({'id': graph_id.uri, 'uri': f'{endpoint}graph/{graph_id.uri}.nt'})
                graph_path = os.path.join(self._graphs_folder, f'{graph_id.uri}.nt')
                g.serialize(destination=graph_path, format='nt')
            
        
        return {'metadata': graphs}
            
    
    def __create_rdf_values(self, valuelist: List[str]):
        rdfvalues = []
        for value in valuelist:
            if value:
                rdfvalues.append(RDFTermFactory.create_rdf_term(value))
        
        return rdfvalues
    
    def get_graph(self, graph_id: str) -> Graph:
        
        graph_file = os.path.join(self._graphs_folder, graph_id)
        if os.path.exists(graph_file):
            g = Graph()
            g.parse(graph_file)
            return g
        else:
            return None
        
    def delete_graph(self, graph_id: str) -> bool:
        
        graph_file = os.path.join(self._graphs_folder, graph_id)
        if os.path.exists(graph_file):
            os.remove(graph_file)
            return True
        else:
            return False