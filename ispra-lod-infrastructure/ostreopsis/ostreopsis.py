import os
from triplification import Triplifier
from kg_loader import KnowledgeGraphLoader
from utils import Utils

class OstreopsisTriplifier(Triplifier):
    
    '''
        The following protected attributes are declared by the superclass Triplifier:
         - self._dataset -> the name of the dataset
         - self._rml_path -> the path to the RML mapping files
         - self._data_path -> the path to CSV data files.
    '''
    def __init__(self, year : int):
        
        functions_dictionary = {
            'round_coord': Utils.round_coord
            }
        
        super().__init__('ostreopsis', functions_dictionary)
        self._dirty_data_path = os.path.join('ostreopsis', 'v2', 'dirtydata')

        self._conf_vars.update({"year": year})
        
        
    def _dataset_initialisation(self, dirty_data_path: str, data_path: str) -> None:
        print("Ostreopsis preprocessing...")
        
        KnowledgeGraphLoader.convert_utf8(dirty_data_path, data_path)
        
        print("\t preprocessing completed.")
   
    def get_graph_iri(self):
        return 'https://w3id.org/italia/env/ld/ostreopsis'
    
