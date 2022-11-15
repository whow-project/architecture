from api.api import Mapper
from pyrml import RMLConverter
import uuid
import os
import glob
import shutil


from rdflib import Graph
from pelix.ipopo.decorators import ComponentFactory, Instantiate, Validate, Provides, Requires, Property

import asyncio
import websockets
import tarfile

@ComponentFactory("mapping-factory")
@Property('_rml_folder', 'rml.folder', '/Users/andrea/airflow/rml')
@Property('_graphs_folder', 'graphs.folder', './mappers/graphs')
@Provides("rml-mapper")
@Instantiate("pyrml-rml-mapper")
class PYRMLMapper(Mapper):
    
    @Validate
    def validate(self, context):
        print('pyRML engine is active!')
    
    
    def map(self):
        
        rml_maps = [rml_map for rml_map in glob.iglob(f'{self._rml_folder}/*.ttl')]
        
        print(f'RML maps {rml_maps} - {self._rml_folder}')
        graphs = []
        
        for rml_map in rml_maps:
            rml_mapper: RMLConverter = RMLConverter.get_instance()
            g: Graph = rml_mapper.convert(rml_map)
            
            if not os.path.exists(self._graphs_folder):
                os.makedirs(self._graphs_folder)
                
            graph_id = uuid.uuid4()
            
            graph_path = os.path.join(self._graphs_folder, f'{graph_id}.nt')
            g.serialize(destination=graph_path, format='nt')
            
            graphs.append(graph_path)
            del(rml_mapper)
        
        graph_id = str(uuid.uuid4())
        tar = tarfile.open(f'{os.path.join(self._graphs_folder, graph_id)}.tar.gz', 'w:gz')
        for graph_path in graphs:
            print(f'Graph path {graph_path}')
            path, file_name = os.path.split(graph_path)
            tar.add(graph_path, arcname=file_name)
            
            tar.close()
                    
            #os.remove(graph_path)
            
            
        return f'{os.path.join(self._graphs_folder, graph_id)}.tar.gz' 
        
        