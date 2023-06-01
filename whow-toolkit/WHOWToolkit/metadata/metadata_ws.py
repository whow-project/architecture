from api.api import Configuration, MetadataCreator, MetadataInput, WebSocketComponent, Reference 
from rdflib.graph import Graph
from pelix.ipopo.decorators import Validate, ComponentFactory, Property, Requires, Provides, Instantiate
import uuid
from rdflib.term import URIRef
from rdflib.namespace._DCAT import DCAT
from rdflib.namespace._RDF import RDF
from rdflib.namespace._DCTERMS import DCTERMS
import os
import json


@ComponentFactory("metadata-websocket-factory")
@Property('_path', 'websocketcomponent.path', '/metadating')
@Requires('_metadata_creator', 'metadata')
@Provides('websocketcomponent')
@Instantiate("metadata-websocket-inst")
class DCATWebSocketComponent(WebSocketComponent):
    
    def __init__(self):
        super().__init__(self._path)
    
    @Validate
    def validate(self, context):
        
        self.__conf = Configuration('./metadata/conf/props.json')
        self._graphs_location = self.__conf.get_property('graphs.location')
        
        endpoint = self.__conf.get_property('http.endpoint')
        self._http_endpoint = endpoint if endpoint.endswith('/') else endpoint + '/' 
        
        if not os.path.exists(self._graphs_location):
            os.makedirs(self._graphs_location)
    
    def execute(self, message: str, *args, **kwargs) -> str:
        
        _input = json.loads(message)
        
        print(f'Metadata WS received {_input}')
        
        if 'meta' and 'graphs' in _input:
            
            meta = _input['meta']
            
            graphs = _input['graphs']
            
            confs = {conf['graph_id']: conf for conf in meta}
            
            for graph in graphs:
                if graph['id'] in confs:
                    confs[graph['id']]['graph_uri'] = Reference(graph['uri'])
                    confs[graph['id']]['access_url'] = Reference(confs[graph['id']]['accessURL'])
                    del(confs[graph['id']]['graph_id'])
                    del(confs[graph['id']]['accessURL'])
                    
                    if 'dataset' in confs[graph['id']]:
                        confs[graph['id']]['dataset'] = Reference(confs[graph['id']]['dataset'])
                        
                    if 'distribution' in confs[graph['id']]:
                        confs[graph['id']]['distribution'] = Reference(confs[graph['id']]['distribution'])  
             
            
            out_graphs = []
        
            for _id, conf in confs.items():
                _input = MetadataInput.from_dict(conf)
            
                g = self._metadata_creator.create_metadata(_input)
                
                graph_path = os.path.join(self._graphs_location, f'{_id}.nt')
                g.serialize(destination=graph_path, format='nt')
                
                out_graphs.append({'id': _id, 'uri': conf['graph_uri'].uri, 'dcat': f'{self._http_endpoint}{_id}'})
            
        
            output = {'status': 'success', 'content': out_graphs}
            
            return json.dumps(output)
        
        else:
            output = {'status': 'error'}
            
            return json.dumps(output)
        
                