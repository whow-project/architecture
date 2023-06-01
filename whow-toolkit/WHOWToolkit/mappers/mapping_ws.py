import json

from pelix.ipopo.decorators import ComponentFactory, Property, Requires, Provides, Instantiate, Validate

from rdflib import Graph, URIRef, Literal, RDF, RDFS, DCAT, DCTERMS
from rdflib.namespace import Namespace

from api.api import DataCollection, DCATCatalog, WebSocketComponent, MapperInput


@ComponentFactory("mapper-websocket-factory")
@Property('_path', 'websocketcomponent.path', '/mapping')
@Requires('_mapper','mapper')
@Provides('websocketcomponent')
@Instantiate("mapper-websocket-inst")
class MappingWebSocketComponent(WebSocketComponent):

    def __init__(self):
        super().__init__(self._path)
        
    @Validate
    def validate(self, context):
        print('MappingWebSocketComponent is active!')
        
    '''
    
    message = {
    
        'title': 'Some title for the catalog',
        'description': 'Some description for the catalog',
        'distributions': ['uri'*],
        'store': true|false
    
    }
    
    '''
    def execute(self, message: str, *args, **kwargs) -> str:
            
        _input = json.loads(message)
        
        print(f'Mapper input message {_input}')
        
        out = self._mapper.map(MapperInput.from_dict(_input))
        
        ret = {"status": "success", "content": out}
        
        return json.dumps(ret)