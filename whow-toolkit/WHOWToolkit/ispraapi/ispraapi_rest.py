import os

from flask.views import MethodView
from pelix.ipopo.decorators import ComponentFactory, Property, Provides, Instantiate, Validate
from pelix.framework import FrameworkFactory
from pelix.utilities import use_service
from flask import request

from rdflib import Graph

@ComponentFactory("ispra-web-factory")
@Property('_path', 'webcomponent.path', '/ispra/<name>')
@Provides('webcomponent')
@Instantiate("ispra-web-inst")
class ISPRAWebExample(MethodView):
    
    def __init__(self):
        self.__conf = None
        
    @Validate
    def validate(self, context):
        print('ISPRA Web is active!')
    
    def get(self, name):
        
        supported_mime_types = ('text/html', 'text/plain', 'application/json')
        
        content_types = [ctype for ctype in request.accept_mimetypes.values()]
            
        if any(item in supported_mime_types for item in content_types):
            if 'text/plain' in content_types:
                return f'Hello, {name}!'
            elif 'text/html' in content_types:
                return f'<h1>Hello, {name}!</h1>'
            elif 'application/json' in content_types:
                return '{"message": "Hello, {'+name+'}!"}'
            
        else:
            return "Mime type not acceptable", 406
        