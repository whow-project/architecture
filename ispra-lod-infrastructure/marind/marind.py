from builtins import staticmethod
import os, re, csv
import pandas as pd
import datetime as dt
from pyrml import TermUtils
from triplification import Triplifier, UtilsFunctions
from kg_loader import KnowledgeGraphLoader
from utils import Utils


UNIT_OF_MEASURES_STAZ = None

class Functions():

    @staticmethod
    def get_unit_of_measure(metric, lang, iri=False):
        
        if iri:
            return TermUtils.irify(UNIT_OF_MEASURES[metric]["Unit_EN"].lower())
        elif lang == 'symbol':
            return UNIT_OF_MEASURES[metric]["Unit"]
        elif lang == 'it':
            return UNIT_OF_MEASURES[metric]["Unit_IT"]
        else:
            return UNIT_OF_MEASURES[metric]["Unit_EN"]


class MarIndTriplifier(Triplifier):
    
    '''
        The following protected attributes are declared by the superclass Triplifier:
         - self._dataset -> the name of the dataset
         - self._rml_path -> the path to the RML mapping files
         - self._data_path -> the path to CSV data files.
    '''

    def __init__(self, year : int):
        
        functions_dictionary = {
            'label_it': Utils.label_it,
            'label_en': Utils.label_en,
            'get_unit_of_measure': Functions.get_unit_of_measure
        }

        super().__init__('marind', functions_dictionary)
        self._dirty_data_path = os.path.join('data', 'marind', 'v2', 'dirtydata')
        self._data_path = os.path.join('data', 'marind', 'v2', 'data')
        self._conf_vars.update({"year": year})


    def _dataset_initialisation(self, dirty_data_path: str, data_path: str) -> None:

        print('marind', "preprocessing...")
        KnowledgeGraphLoader.convert_utf8(dirty_data_path, data_path)

        # df = pd.read_csv(os.path.join(data_path, "Descrizione_campi.csv"), sep=None, engine='python', iterator=True)
        # sep = df._engine.data.dialect.delimiter
        # df.close()

        # global UNIT_OF_MEASURES

        # units_df = pd.read_csv(os.path.join(data_path, "Descrizione_campi.csv"), sep=sep)[["Campo", "Unit_EN", "Unit_IT", "Unit"]].set_index('Campo')
        # UNIT_OF_MEASURES = units_df.to_dict(orient="index")
        # del units_df

        print("\t preprocessing completed.")


    def get_graph_iri(self, key_name : str):
        return 'https://w3id.org/italia/env/ld/' + key_name
    

    def get_dataset_name(self, key_name : str):
        return key_name
    
