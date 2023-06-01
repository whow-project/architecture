from api.api import Mapper, HTTPResource, RESTApp, MapperInput
from pyrml import RMLConverter
from flask.views import MethodView
from flask import send_file
import uuid
import os
import glob
import shutil
import json

from typing import Dict


from rdflib import Graph
from pelix.ipopo.decorators import ComponentFactory, Instantiate, Validate, Provides, Requires, Property

import asyncio
import websockets
import tarfile

import urllib.request


class MappingConfiguration():
    
    INSTANCE = None
    
    def __init__(self):
        with open('./mappers/conf/props.json') as f:
            self.__js = json.load(f)
            
    def get_property(self, prop_name):
        return self.__js[prop_name]
    
    @classmethod
    def get_instance(cls):
        
        if not cls.INSTANCE:
            cls.INSTANCE = MappingConfiguration()
        
        return cls.INSTANCE
        
        
            


@ComponentFactory("mapping-factory")
@Property('_rml_folder', 'rml.folder', '')
@Property('_graphs_folder', 'graphs.folder', '')
@Property('_http_endpoint', 'http.endpoint', '')
@Provides("mapper")
@Instantiate("pyrml-rml-mapper")
class PYRMLMapper(Mapper):
    
    @Validate
    def validate(self, context):
        print('pyRML engine is active!')
        self.__conf = MappingConfiguration.get_instance()
        
        self._rml_folder = self.__conf.get_property('rml.folder')
        self._graphs_folder = self.__conf.get_property('graphs.folder')
        self._http_endpoint = self.__conf.get_property('http.endpoint')
    
    '''
    input:
    
        {"data": [
            {"id": "some_id", 
             "filename": "soma_file_name",
             "uri": "some_file_uri"}]
        "rml_refs": [list_or_rml_uris]
        }
    
    '''
    
    def map(self, input: MapperInput, *args, **kwargs):
        
        if not os.path.exists(self._graphs_folder):
            os.makedirs(self._graphs_folder)
            
        if not os.path.exists(self._rml_folder):
            os.makedirs(self._rml_folder)
        
        #with urllib.request.urlopen(input_json) as url:
        #    js = json.load(url)
        #js = json.load(input_json)
    
        data = input.data_sources
        mapping_confs = input.mapping_confs
        
        
        template_vars = dict()
        for in_data in data:
            template_vars[in_data.identifier] = in_data.reference.uri
            
        #rml_maps = [rml_map for rml_map in glob.iglob(f'{self._rml_folder}/*.ttl')]
        
        print(f'RML maps: {mapping_confs}')
        print(f'Template vars: {template_vars}')
        graphs = []
        
        for mapping_conf in mapping_confs:
            
            graph_id = mapping_conf.graph_id
            
            
            g: Graph = Graph()
            for rml_map in mapping_conf.rmls:
            
                rml_map_file = f'{self._rml_folder}/{str(uuid.uuid4())}.ttl'
                
                print(f'RML MAP URI {rml_map.uri}')
                urllib.request.urlretrieve(rml_map.uri, rml_map_file)
                
                rml_mapper: RMLConverter = RMLConverter.get_instance()
                g += rml_mapper.convert(rml_map_file, template_vars=template_vars)
                
                #graph_id = uuid.uuid4()
                
                del(rml_mapper)
                
                os.remove(rml_map_file)
            
            
            endpoint = self._http_endpoint if self._http_endpoint.endswith('/') else self._http_endpoint + '/'
            graphs.append({'id': graph_id, 'uri': f'{endpoint}{graph_id}.nt'})
            graph_path = os.path.join(self._graphs_folder, f'{graph_id}.nt')
            g.serialize(destination=graph_path, format='nt')
        
        return {'graphs': graphs}
    