import os
from triplification import Triplifier, UtilsFunctions
from kg_loader import KnowledgeGraphLoader



class CommonTriplifier(Triplifier):
    
    '''
        The following protected attributes are declared by the superclass Triplifier:
         - self._dataset -> the name of the dataset
         - self._rml_path -> the path to the RML mapping files
         - self._data_path -> the path to CSV data files.
    '''
    def __init__(self):
       
        super().__init__('common')
        self._dirty_data_path = os.path.join('data', 'common', 'v2', 'dirtydata')
        self._data_path = os.path.join('data', 'common', 'v2', 'data')
     

    def _dataset_initialisation(self, dirty_data_path: str, data_path: str) -> None:

        print("Common preprocessing...")
        KnowledgeGraphLoader.convert_utf8(dirty_data_path, data_path)
        print("\t preprocessing completed.")