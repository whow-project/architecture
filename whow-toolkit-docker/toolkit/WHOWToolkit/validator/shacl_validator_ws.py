from pelix.ipopo.decorators import ComponentFactory, Property, Requires, Provides, Instantiate, Validate

from api.api import ValidatorInput, Validator, WebSocketComponent
import logging
import json

@ComponentFactory("validator-websocket-factory")
@Property('_path', 'websocketcomponent.path', '/validation')
@Requires('_validator','validator')
@Provides('websocketcomponent')
@Instantiate("validator-websocket-inst")
class ValidatorWebSocketComponent(WebSocketComponent):

    def __init__(self):
        super().__init__(self._path)
        
    @Validate
    def validate(self, context):
        print('ValidatorWebSocketComponent is active!')
        
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
        
        logging.info(f'Validator input message {_input}')
        
        out = self._validator.do_job(ValidatorInput.from_dict(_input))
        
        out = {**_input, 'validation': out}
        
        ret = {"status": "success", "content": out}
        
        return json.dumps(ret)