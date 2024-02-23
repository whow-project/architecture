import os

from api.api import WebView
from triplifier.triplifier_core import MappingConfiguration
from flask.helpers import send_file
from flask.views import MethodView
from pelix.ipopo.decorators import ComponentFactory, Property, Provides, Instantiate, Validate
from pelix.framework import FrameworkFactory
from pelix.utilities import use_service
from flask import request, abort, render_template

from rdflib import Graph


@ComponentFactory("mapping-webview-factory")
@Property('_name', 'webcomponent.name', 'triplifier')
@Property('_path', 'webcomponent.path', '/')
@Property('_context', 'webcomponent.context', __name__)
@Provides('webviewcomponent')
@Instantiate("triplifier-webview-inst")
class TriplifierWeb(WebView):
    
    def __init__(self):
        super().__init__()
        self.__conf = MappingConfiguration.get_instance()
        
    def get(self):
        
        return render_template('triplifier.html', services=self.webservices)

@ComponentFactory("mapping-web-factory")
@Property('_name', 'webcomponent.name', 'mapper')
@Property('_path', 'webcomponent.path', '/<graph>')
@Property('_context', 'webcomponent.context', __name__)
@Provides('webcomponent')
@Instantiate("mapper-web-inst")
class PYRMLMapperWeb(MethodView):
    
    def __init__(self):
        self.__conf = MappingConfiguration.get_instance()
        
    @Validate
    def validate(self, context):
        print('PYRMLMapperWeb is active!')
    
    def get(self, graph):
        
        graph_file = os.path.join(self.__conf.get_property('graphs.folder'), graph)
        
        if os.path.exists(graph_file):
            return send_file(graph_file)
        else:
            abort(404)
        
    def delete(self, graph):
        graph_file = os.path.join(self.__conf.get_property('graphs.folder'), graph)
        
        if os.path.exists(graph_file):
            os.remove(graph_file)
            return "Success", 200
        else:
            abort(404)
            
            
            
@ComponentFactory("rml-store-web-factory")
@Property('_name', 'webcomponent.name', 'rmlstore')
@Property('_path', 'webcomponent.path', '/mapper/rml/<graph>')
@Property('_context', 'webcomponent.context', __name__)
@Provides('webcomponent')
@Instantiate("rml-store-web-inst")
class RMLStoreWeb(MethodView):
    
    def __init__(self):
        self.__conf = MappingConfiguration.get_instance()
        
    @Validate
    def validate(self, context):
        print('RMLStoreWeb is active!')
    
    def get(self, graph):
        
        ctx = FrameworkFactory.get_framework().get_bundle_context()
        reference = ctx.get_service_reference('mapper')
        
        supported_mime_types = ('application/rdf+xml', 'text/turtle', 'application/json-ld', 'application/json', 'application/n-triples')
        
        content_types = [ctype for ctype in request.accept_mimetypes.values()]
            
        if any(item in supported_mime_types for item in content_types):
        
            with use_service(ctx, reference) as mapper:
                g : Graph = mapper.get_rml(graph)
                return g.serialize(format=content_types[0]), 200
            
        else:
            return "Mime type not acceptable", 406
            
    def post(self, graph):
        
        ctx = FrameworkFactory.get_framework().get_bundle_context()
        reference = ctx.get_service_reference('mapper')
        
        supported_mime_types = ('application/rdf+rml', 'text/turtle', 'application/json-ld', 'text', 'application/n-triples')
            
        content_type = request.content_type
        print(f'Content type: {content_type}')
        
        if content_type in supported_mime_types:
            with use_service(ctx, reference) as mapper:
        
                data = request.data.decode('utf-8')
                
                g = Graph()
                g.parse(format=content_type, data=data)
                
                ret = mapper.save_rml(graph, g)
                
                if ret:
                    return "Success", 200
                else:
                    return "An RML mapping with the same ID already exists.", 409
        else:
            return "Mime type not acceptable", 406
        
    def delete(self, graph):
        
        ctx = FrameworkFactory.get_framework().get_bundle_context()
        reference = ctx.get_service_reference('mapper')
        
        with use_service(ctx, reference) as mapper:
            mapper.delete_rml(graph)
            return "Success", 200