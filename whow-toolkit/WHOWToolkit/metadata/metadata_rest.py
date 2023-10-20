import os

from api.api import Configuration
from flask.helpers import send_file, abort
from flask.views import MethodView
from pelix.ipopo.decorators import ComponentFactory, Property, Provides, Instantiate, Validate
from pelix.framework import FrameworkFactory
from pelix.utilities import use_service
from flask import request

from rdflib import Graph

@ComponentFactory("metadata-graph-web-factory")
@Property('_path', 'webcomponent.path', '/metadata-mgr/graph/<graph_id>')
@Provides('webcomponent')
@Instantiate("metadata-graph-web-inst")
class MetadataWeb(MethodView):
    
    def __init__(self):
        self.__conf = Configuration('./metadata/conf/props.json')
        
    @Validate
    def validate(self, context):
        print('Web Medata manager is active!')
    
    def get(self, graph_id):
        
        supported_mime_types = ('application/rdf+xml', 'text/turtle', 'application/json-ld', 'application/json', 'application/n-triples')
        
        content_types = [ctype for ctype in request.accept_mimetypes.values()]
            
        if any(item in supported_mime_types for item in content_types):
        
            ctx = FrameworkFactory.get_framework().get_bundle_context()
            reference = ctx.get_service_reference('metadata')
        
            with use_service(ctx, reference) as metadata_mgr:
                g : Graph = metadata_mgr.get_graph(graph_id)
                
                if g:
                    return g.serialize(format=content_types[0]), 200
                else:
                    return f'The RDF graph with ID {graph_id} does not exist.', 404
                
        else:
            return "Mime type not acceptable", 406
        
    def delete(self, graph_id):
        
        ctx = FrameworkFactory.get_framework().get_bundle_context()
        reference = ctx.get_service_reference('metadata')
        
        with use_service(ctx, reference) as metadata_mgr:
            out : bool = metadata_mgr.delete_graph(graph_id)
            if out:
                return "Success", 200
            else:
                return f'The RDF graph with ID {graph_id} does not exist.', 404
        