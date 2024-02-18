from pelix.ipopo.decorators import ComponentFactory, Instantiate, Validate, Provides, Property
import pyodbc

from api.api import TriplestoreManager, Input, Configuration
from rdflib import URIRef, Graph
import os
import logging

@ComponentFactory("triplestore-factory")
@Property('_graph_folder', 'graph.folder', '')
@Provides("triplestore-manager")
@Instantiate("virtuoso-triplestore-manager")
class VirtuosoTriplestoreManager(TriplestoreManager):
    
    @Validate
    def validate(self, context):
        print('Virtuoso manager is active!')
        
        self.__conf = Configuration('./triplestores/conf/props.json')
        self._graph_folder= self.__conf.get_property('graph.folder')
        
        if not os.path.exists(self._graph_folder):
            os.makedirs(self._graph_folder)
        
        
    def do_job(self, input: Input, *args, **kwargs):
        
        try:
            files = []
            for graph in _input['graphs']:
                uri: str = graph['uri']
                pos = uri.rfind('/')
                filename = uri[pos+1:]
                
                f = os.path.join(self._graph_folder, filename)
                
                urllib.request.urlretrieve(uri, f)
                
                logging.info(f'Downloaded {uri} to {f}')
                files.append(f)
                
            self.load_graphs()
            for f in files:
                os.remove(f)
        except Exception as e:
            return False
            
        return True
        
        
        
        
    def load_graphs(self):
        q = f"ld_dir_all('{self._graph_folder}', '*.nt', 'data')"
        self.query(q)
        q = f"ld_dir_all('{self._graph_folder}', '*.tar.gz', 'data')"
        self.query(q)
        self.query('rdf_loader_run()')
        self.query('CHECKPOINT')
        self.query('COMMIT WORK')
        self.query('CHECKPOINT')
        
        print('Loaded graphs into Virtuoso!')

    def query(self, querystr: str):
        cnxn = pyodbc.connect('DSN=VIRTUOSO VOS;UID=dba;PWD=dba')
        
        rs = cnxn.execute(querystr)
        
        return rs
    
    def add_graph(self, g: Graph, graph_identifier: URIRef):
        Virtuoso = plugin("Virtuoso", Store)
        
        store = Virtuoso("DSN=VOS;UID=dba;PWD=dba;WideAsUTF16=Y")
        
        graph = Graph(store,identifier = graph_identifier)
        
        for triple in g:
            graph.add(triple)
            
    def get_graph(self, graph_identifier):
        
        Virtuoso = plugin("Virtuoso", Store)
        store = Virtuoso("DSN=VOS;UID=dba;PWD=dba;WideAsUTF16=Y")
        return Graph(store,identifier = graph_identifier)
    