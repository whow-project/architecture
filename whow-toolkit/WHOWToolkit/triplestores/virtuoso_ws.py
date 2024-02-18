from api.api import Configuration, TriplestoreManager, WebSocketComponent, Reference 
from rdflib import Graph, URIRef, DCAT, RDF, DCTERMS
from pelix.ipopo.decorators import Validate, ComponentFactory, Property, Requires, Provides, Instantiate
import uuid

import os
import json
import logging


@ComponentFactory("triplestore-websocket-factory")
@Property('_path', 'websocketcomponent.path', '/triplestore')
@Requires('_triplestore_manager', 'triplestore-manager')
@Provides('websocketcomponent')
@Instantiate("triplestore-websocket-inst")
class VirtuosoWebSocketComponent(WebSocketComponent):
    
    def __init__(self):
        super().__init__(self._path)
    
    @Validate
    def validate(self, context):
        
        self.__conf = Configuration('./triplestores/conf/props.json')
        endpoint = self.__conf.get_property('http.endpoint')
        self._http_endpoint = endpoint if endpoint.endswith('/') else endpoint + '/'
        
        self._graph_folder= self.__conf.get_property('graph.folder') 
        
    
    def execute(self, message: str, *args, **kwargs) -> str:
        
        _input = json.loads(message)
        logging.info(f'Triplestore WS received {_input}')
        
        out = self._triplestore_manager.do_job(_input['graphs'])
        
        if out:
            ret = {"status": "success", "content": _input}
        else:
            ret = {"status": "failure", "content": _input}
        
        return json.dumps(ret)