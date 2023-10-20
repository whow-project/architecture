import json

from pelix.ipopo.decorators import ComponentFactory, Property, Requires, Provides, Instantiate, Validate

from rdflib import Graph, URIRef, Literal, RDF, RDFS, DCAT, DCTERMS
from rdflib.namespace import Namespace

from api.api import DataCollection, DCATCatalog, WebSocketComponent, MapperInput


@ComponentFactory("reasoning-websocket-factory")
@Property('_path', 'websocketcomponent.path', '/reasoning')
@Requires('_reasoner','reasoner')
@Provides('websocketcomponent')
@Instantiate("reasoner-websocket-inst")
class ReasoningWebSocketComponent(WebSocketComponent):

    def __init__(self):
        super().__init__(self._path)
        
    @Validate
    def validate(self, context):
        print('ReasoningWebSocketComponent is active!')
        
    '''
    
    message = {
        reasoning: {
            'graph_id': 'Some graph ID',
            'ontologies': [ontology_IRI+]
        }
    }
    
    '''
    def execute(self, message: str, *args, **kwargs) -> str:
            
        _input = json.loads(message)
        
        print(f'Reasoner input message {_input}')
        
        out = self._reasoner.do_reasoning()
        
        ret = {"status": "success", "content": out}
        
        return json.dumps(ret)