import json

from pelix.ipopo.decorators import ComponentFactory, Property, Provides, Instantiate, Requires, Validate
from rdflib import URIRef, Literal, RDF, DCAT, DCTERMS

from api.api import WebSocketComponent, WHOWFlow, DataCollection
from rdflib.namespace import Namespace


@ComponentFactory("preprocessor-websocket-factory")
@Property('_path', 'websocketcomponent.path', '/preprocessor')
@Requires('_cleanser','cleanser')
@Provides('websocketcomponent')
@Instantiate("preprocessor-websocket-inst")
class CleansingWebSocketComponent(WebSocketComponent):

    def __init__(self):
        super().__init__(self._path)
        
    @Validate
    def validate(self, context):
        print('CleansingWebSocketComponent is active!')
        
    '''
    
    message = {
    
        "data": [
            {
                "id": "ANY_ID",
                "filename": "NAME",
                "uri": "URI"
            }*
        ]}
    
    '''
    def execute(self, message: str, *args, **kwargs) -> str:
            
            whow_data = Namespace("https://w3id.org/whow/data/")
            
            _input = json.loads(message)
            
            print(f'Data cleansing input {_input}.')
            
            datacollection = DataCollection.from_dict(_input)
            
            out = self._cleanser.do_job(datacollection)
            
            out_message = {'status': 'success', 'content': out}
            return json.dumps(out_message)
        
        