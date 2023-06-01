import os

from mappers.mapping_core import MappingConfiguration
from flask.helpers import send_file
from flask.views import MethodView
from pelix.ipopo.decorators import ComponentFactory, Property, Provides, Instantiate, Validate


@ComponentFactory("mapping-web-factory")
@Property('_path', 'webcomponent.path', '/mapper/<graph>')
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