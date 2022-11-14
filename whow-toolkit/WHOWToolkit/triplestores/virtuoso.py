from pelix.ipopo.decorators import ComponentFactory, Instantiate, Validate, Provides, Property
import pyodbc

from api.api import TriplestoreManager
from curses.ascii import RS


@ComponentFactory("triplestore-factory")
@Property('_graphs_folder', 'graphs.folder', '/graphs')
@Provides("triplestore-manager")
@Instantiate("virtuoso-triplestore-manager")
class VirtuosoTriplestoreManager(TriplestoreManager):
    
    @Validate
    def validate(self, context):
        print('Virtuoso manager is active!')
        
        
    def load_graphs(self):
        q = f"ld_dir_all('{self._graphs_folder}', '*.nt', 'data')"
        self.query(q)
        self.query('rdf_loader_run()')
        self.query('CHECKPOINT')
        self.query('COMMIT WORK')
        self.query('CHECKPOINT')
        
        print('Loaded graphs into Virtuoso!')

    def query(self, querystr: str):
        cnxn = pyodbc.connect('DSN=VIRTUOSO VOS;UID=dba;PWD=dba')
        
        rs = cnxn.execute(querystr)
        
        return RS
    
vtm = VirtuosoTriplestoreManager()
vtm.query('SELECT * FROM LOAD_LIST')